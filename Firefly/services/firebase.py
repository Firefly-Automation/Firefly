import configparser
import copy
import json
from os import system

import pyrebase
import requests

from Firefly import aliases, logging, scheduler
from Firefly.const import API_ALEXA_VIEW, API_FIREBASE_VIEW, SERVICE_CONFIG_FILE, SOURCE_LOCATION, SOURCE_TIME, TYPE_AUTOMATION, TYPE_DEVICE
from Firefly.helpers.service import Command, Request, Service
from Firefly.services.api_ai import apiai_command_reply

FIREBASE_LOCATION_STATUS_PATH = 'locationStatus'
FIREBASE_DEVICE_VIEWS = 'deviceViews'
FIREBASE_DEVICE_STATUS = 'deviceStatus'
FIREBASE_ALIASES = 'aliases'

# This is the action when status messages are updated
STATUS_MESSAGE_UPDATED = {
  'status_message': 'updated'
}


def internet_up():
  return system("ping -c 1 8.8.8.8") == 0


TITLE = 'Firebase Service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_firebase'
COMMANDS = ['push', 'refresh', 'get_api_id']
REQUESTS = []

SECTION = 'FIREBASE'


# TODO: Setup function should get the config from the service config file. If the
# required params are not in the config file then it should log and error message
# and abort install

# TODO: push this data to location weather info.. this could be useful

def Setup(firefly, package, **kwargs):
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)
  enable = config.getboolean(SECTION, 'enable', fallback=False)
  if enable is False:
    return False
  api_key = config.get(SECTION, 'api_key', fallback=None)
  auth_domain = config.get(SECTION, 'auth_domain', fallback=None)
  database_url = config.get(SECTION, 'database_url', fallback=None)
  email = config.get(SECTION, 'email', fallback=None)
  password = config.get(SECTION, 'password', fallback=None)
  storage_bucket = config.get(SECTION, 'storage_bucket', fallback=None)
  home_id = config.get(SECTION, 'home_id', fallback=None)
  if api_key is None:
    logging.error('firebase error')  # TODO Make this error code
    return False
  firebase = Firebase(firefly, package, api_key=api_key, auth_domain=auth_domain, database_url=database_url, email=email, password=password, storage_bucket=storage_bucket, home_id=home_id)
  firefly.install_component(firebase)
  return True


class Firebase(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self.api_key = kwargs.get('api_key')
    self.auth_domain = kwargs.get('auth_domain')
    self.database_url = kwargs.get('database_url')
    self.storage_bucket = kwargs.get('storage_bucket')
    self.email = kwargs.get('email')
    self.password = kwargs.get('password')

    self.home_id = kwargs.get('home_id')

    self.add_command('push', self.push)
    self.add_command('refresh', self.refresh_all)
    self.add_command('get_api_id', self.get_api_id)

    self.config = {
      "apiKey":        self.api_key,
      "authDomain":    self.auth_domain,
      "databaseURL":   self.database_url,
      "storageBucket": self.storage_bucket
    }

    self.firebase = pyrebase.initialize_app(self.config)

    # Get a reference to the auth service
    self.auth = self.firebase.auth()

    # Log the user in
    self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
    self.uid = self.user['localId']
    self.id_token = self.user['idToken']

    # Get a reference to the database service
    self.db = self.firebase.database()

    if self.home_id is None:
      self.register_home()

    scheduler.runEveryM(30, self.refresh_user)
    scheduler.runEveryM(20, self.refresh_all)
    scheduler.runInS(20, self.refresh_all)

    self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.command_stream_handler, self.id_token)
    self.commandReplyStream = self.db.child('homeStatus').child(self.home_id).child('commandReply').stream(self.command_reply, self.id_token)

  def register_home(self):
    register_url = 'https://us-central1-firefly-beta-cdb9d.cloudfunctions.net/registerHome'
    return_data = requests.post(register_url, data={
      'uid': self.uid
    }).json()
    self.home_id = return_data.get('home_id')

    if self.home_id is None:
      logging.notify('error registering home')
      return

    config = configparser.ConfigParser()
    config.read(SERVICE_CONFIG_FILE)
    config.set(SECTION, r'home_id', str(self.home_id))
    with open(SERVICE_CONFIG_FILE, 'w') as configfile:
      config.write(configfile)
    logging.info('Config file for hue has been updated.')

  def refresh_stream(self):
    if not internet_up():
      logging.error('[FIREBASE REFRESH STREAM] Internet is down')
      scheduler.runInM(1, self.refresh_stream, 'firebase_internet_down_refresh_stream')
      return

    self.stream.close()
    self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.command_stream_handler, self.id_token)
    self.commandReplyStream.close()
    self.commandReplyStream = self.db.child('homeStatus').child(self.home_id).child('commandReply').stream(self.command_reply, self.id_token)

  def command_reply(self, message):
    if not message['data']:
      return
    if message['data'].get('reply') is not None or message.get('reply') is not None:
      return
    key = message['path'][1:]
    if 'reply' in key or 'speech' in key:
      return
    try:
      reply = apiai_command_reply(self.firefly, message['data'])
      self.db.child('homeStatus').child(self.home_id).child('commandReply').child(key).child('reply').set(reply, self.id_token)
    except Exception as e:
      print(str(e))

  def firebase_send_command(self, ff_id, command):
    ''' process and send command from firebase commands

    Args:
      ff_id: device to send command to
      command: command to be sent

    Returns:

    '''
    logging.info('[FIREBASE SEND COMMAND] : %s:%s' % (str(ff_id), str(command)))

    # Location is a special case.
    if ff_id == 'location':
      if type(command) is not dict:
        return
      for command_string, command_args in command.items():
        send_command = Command(ff_id, 'web_api', command_string, **command_args)
        self.firefly.location.process_command(send_command)

    if type(command) is str:
      send_command = Command(ff_id, 'web_api', command)
      logging.info('FIREBASE SENDING COMMAND: %s ' % str(send_command))
      self.firefly.send_command(send_command)

      if command == 'delete':
        scheduler.runInS(10, self.update_device_views, job_id='firebase_refresh')
      return

    # TODO Handle install package command
    # if list(command.keys())[0] == 'install_package':
    #   self.firefly.install_package(**dict(list(command.values())[0]))

    if type(command) is dict:
      for command_string, command_args in command.items():
        send_command = Command(ff_id, 'web_api', command_string, **command_args)
        logging.info('FIREBASE SENDING COMMAND: %s ' % str(send_command))
        self.firefly.send_command(send_command)
        return

  def command_stream_handler(self, message):
    ''' Handle commands sent from the ui

    Args:
      message: message from command stream

    Returns:

    '''
    try:
      logging.message('FIREBASE MESSAGE: %s ' % str(message))
      # Return if no data
      if message['data'] is None:
        return

      if message['path'] == '/':
        for ff_id, command in message['data'].items():
          self.firebase_send_command(ff_id, command)
          self.db.child('homeStatus').child(self.home_id).child('commands').child(ff_id).remove(self.id_token)

      else:
        ff_id = message['path'][1:]
        command = message['data']
        self.firebase_send_command(ff_id, command)
        self.db.child('homeStatus').child(self.home_id).child('commands').child(ff_id).remove(self.id_token)

    except Exception as e:
      logging.error('Firebase Stream Error: %s' % str(e))

  def refresh_all(self, **kwargs):
    # Hard-coded refresh all device values
    # TODO use core api for this.
    all_values = {}
    for ff_id, device in self.firefly.components.items():
      try:
        all_values[ff_id] = device.get_all_request_values()
      except:
        pass

    # Nasty json sanitation
    all_values = scrub(all_values)
    all_values = json.dumps(all_values)
    all_values = all_values.replace('null', '')
    all_values = all_values.replace('#', '')
    all_values = all_values.replace('$', '')
    all_values = all_values.replace('/', '_-_')
    all_values = json.loads(all_values)

    try:
      alexa_views = self.get_all_alexa_views('firebase')
      routines = self.get_routines()

      # TODO(zpriddy): Remove old views when new UI is done
      self.db.child("userAlexa").child(self.uid).child("devices").set(alexa_views, self.id_token)
      self.db.child("homeStatus").child(self.home_id).child('devices').update(all_values, self.id_token)
      self.db.child("homeStatus").child(self.home_id).child('routines').set(routines['config'], self.id_token)
      # End of old views

      routine_view = {}
      for r in routines['view']:
        routine_view[r.get('ff_id')] = r

      routine_config = {}
      for r in routines['config']:
        routine_config[r.get('ff_id')] = r

      # Update all devices statuses
      self.update_all_device_status(overwrite=True)

      # This is the new location of routine views [/homeStatus/{homeId}/routineViews]
      self.db.child("homeStatus").child(self.home_id).child('routineViews').set(routine_view, self.id_token)
      self.db.child("homeStatus").child(self.home_id).child('routineConfigs').set(routine_config, self.id_token)

      # This is the new location of location status [/homeStatus/{homeId}/locationStatus]
      self.update_location_status(overwrite=True, update_metadata_timestamp=False)

      # This is the new location of alexa api data [/homeStatus/{homeId}/alexaAPIView]
      self.db.child("homeStatus").child(self.home_id).child('alexaAPIViews').set(alexa_views, self.id_token)

      groups = {}
      groups_state = {}
      for ff_id, group in self.firefly.components.items():
        if group.type != 'GROUP':
          continue
        groups[ff_id] = group.get_metadata()
        groups_state[ff_id] = group.get_all_request_values()

      self.db.child("homeStatus").child(self.home_id).child('groupViews').set(groups, self.id_token)
      self.db.child("homeStatus").child(self.home_id).child('groupStatus').set(groups_state, self.id_token)

      self.update_device_views()

    except Exception as e:
      logging.notify("Firebase 271: %s" % str(e))

  def update_last_metadata_timestamp(self):
    ''' Update the lastMetadataUpdate timestamp

    Returns:

    '''
    self.set_home_status('locationStatus/lastMetadataUpdate', self.firefly.location.now.timestamp())

  def set_home_status(self, path, data, retry=True, **kwargs):
    ''' Function to set homeStatus in firebase

    Args:
      path: path from homeStatus/{homeID}/ that will be set.
      data: data that will be set.

    Returns:

    '''
    try:
      self.db.child("homeStatus").child(self.home_id).child(path).set(data, self.id_token)
      return True
    except Exception as e:
      if not retry:
        return False
      logging.error('[FIREBASE SET HOME STATUS] ERROR: %s' % str(e))
      self.refresh_user()
      return self.set_home_status(path, data, False)

  def update_home_status(self, path, data, retry=True, **kwargs):
    ''' Function to update homeStatus in firebase

    Args:
      path: path from homeStatus/{homeID}/ that will be updateed.
      data: data that will be updateed.

    Returns:

    '''
    try:
      self.db.child("homeStatus").child(self.home_id).child(path).update(data, self.id_token)
      return True
    except Exception as e:
      if not retry:
        return False
      logging.error('[FIREBASE UPDATE HOME STATUS] ERROR: %s' % str(e))
      self.refresh_user()
      return self.update_home_status(path, data, False)

  def update_location_status(self, overwrite=False, update_metadata_timestamp=False, update_status_message=False, **kwargs):
    ''' update the location status in firebase.

    Args:
      overwrite: if true calls set instead of update.
      update_metadata_timestamp: also update metadata timestamp. When calling set without updating the timestamp the timestamp will be removed.
      update_status_message: clear all status messages and inset current status messages
      **kwargs:

    Returns:

    '''
    location_status = self.get_location_status()

    if overwrite:
      self.set_home_status(FIREBASE_LOCATION_STATUS_PATH, location_status)
      if update_metadata_timestamp:
        self.update_last_metadata_timestamp()
      return

    if update_status_message:
      self.set_home_status('%s/statusMessages' % FIREBASE_LOCATION_STATUS_PATH, {})

    self.update_home_status(FIREBASE_LOCATION_STATUS_PATH, location_status)

  def update_device_views(self, **kwargs):
    ''' Update device views metadata for all devices

    Args:
      **kwargs:

    Returns:

    '''
    logging.info('[FIREBASE DEVICE VIEW UPDATE] updating all device views')
    device_views = {}
    devices = self.get_all_component_views('firebase_refresh', filter=TYPE_DEVICE)
    for device in devices:
      device_views[device.get('ff_id', 'unknown')] = device
    self.set_home_status(FIREBASE_DEVICE_VIEWS, device_views)

    #TODO: Remove this
    self.set_home_status('devices', device_views)

    self.update_aliases()
    self.update_last_metadata_timestamp()

  def update_all_device_status(self, overwrite=False, **kwargs):
    # TODO use core api for this.
    all_values = {}
    for ff_id, device in self.firefly.components.items():
      try:
        all_values[ff_id] = device.get_all_request_values()
      except:
        pass

    for device, device_view in all_values.items():
      try:
        if 'PARAMS' in device_view.keys():
          device_view.pop('PARAMS')
        if 'RAW_VALUES' in device_view.keys():
          device_view.pop('RAW_VALUES')
        if 'SENSORS' in device_view.keys():
          device_view.pop('SENSORS')
      except:
        pass

    #TODO Remove this
    self.update_home_status('devices', all_values)

    if overwrite:
      self.set_home_status(FIREBASE_DEVICE_STATUS, all_values)
      return

    self.update_home_status(FIREBASE_DEVICE_STATUS, all_values)

  def update_device_status(self, ff_id, action, **kwargs):
    ''' Update a single device status

    Args:
      ff_id: ff_id of the device to update
      action: the action data to update
      **kwargs:

    Returns:

    '''
    # TODO(zpriddy): Find a better way to do this
    if 'PARAMS' in action.keys():
      return
    if 'RAW_VALUES' in action.keys():
      return
    if 'SENSORS' in action.keys():
      return

    path = '%s/%s' % (FIREBASE_DEVICE_STATUS, ff_id)
    self.update_home_status(path, action)

  def update_aliases(self, **kwargs):
    ''' update all device aliases from firefly.

    Args:
      **kwargs:

    Returns:

    '''
    self.set_home_status(FIREBASE_ALIASES, aliases.aliases)

  def get_routines(self):
    routines = {
      'view':   [],
      'config': []
    }
    for ff_id, d in self.firefly.components.items():
      if d.type == TYPE_AUTOMATION and 'routine' in d._package:
        routines['view'].append(d.export(firebase_view=True))
        routines['config'].append(d.export())
    return routines

  def get_component_view(self, ff_id, source):
    device_request = Request(ff_id, source, API_FIREBASE_VIEW)
    data = self.firefly.components[device_request.ff_id].request(device_request)
    return data

  def get_component_alexa_view(self, ff_id, source):
    device_request = Request(ff_id, source, API_ALEXA_VIEW)
    data = self.firefly.components[device_request.ff_id].request(device_request)
    return data

  def get_all_alexa_views(self, source, filter=TYPE_DEVICE):
    if type(filter) is str:
      filter = [filter]
    views = []
    for ff_id, device in self.firefly.components.items():
      if device.type in filter or filter is None:
        data = self.get_component_alexa_view(ff_id, source)
        if data is not None:
          views.append(data)
    return views

  def get_all_component_views(self, source, filter=None):
    if type(filter) is str:
      filter = [filter]
    views = []
    for ff_id, device in self.firefly.components.items():
      if device.type in filter or filter is None:
        data = self.get_component_view(ff_id, source)
        views.append(data)
    return views

  def get_location_status(self, **kwargs):
    """
    Get the location status.
    Args:
      **kwargs:

    Returns: dict of location status

    """
    now = self.firefly.location.now
    return_data = {
      'time':           {
        'epoch':    now.timestamp(),
        'day':      now.day,
        'month':    now.month,
        'year':     now.year,
        'hour':     now.hour,
        'minute':   now.minute,
        'str':      str(now),
        'timeZone': self.firefly.location.geolocation.timezone
      },
      'location':       {
        'lat':     self.firefly.location.latitude,
        'lon':     self.firefly.location.longitude,
        'address': self.firefly.location.address
      },
      'isDark':         self.firefly.location.isDark,
      'mode':           self.firefly.location.mode,
      'lastMode':       self.firefly.location.lastMode,
      'statusMessages': self.firefly.location.status_messages,
      'modes':          self.firefly.location.modes
    }
    return return_data

  def refresh_user(self):
    ''' Refresh user token and auth

    Returns:

    '''
    logging.info('[FIREBASE] REFRESHING USER')
    if not internet_up():
      logging.error('[FIREBASE REFRESH] Internet seems to be down')
      scheduler.runInM(1, self.refresh_user, 'refresh_user_internet_down')
      return

    try:
      try:
        self.stream.close()
        self.commandReplyStream.close()
      except:
        pass
      self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
      self.id_token = self.user['idToken']
      self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.command_stream_handler, self.id_token)
      self.commandReplyStream = self.db.child('homeStatus').child(self.home_id).child('commandReply').stream(self.command_reply, self.id_token)
    except Exception as e:
      logging.info("Firebase 266: %s" % str(e))
      scheduler.runInH(1, self.refresh_user, 'firebase_refresh_user')
      pass

  def push(self, source, action, retry=True):
    logging.info('[FIREBASE PUSH] Pushing Data: %s: %s' % (str(source), str(action)))
    try:

      # Update time events
      if source == SOURCE_TIME:
        self.update_location_status()
        return

      # Update location events
      if source == SOURCE_LOCATION:
        update_status_message = action == STATUS_MESSAGE_UPDATED
        self.update_location_status(update_status_message=update_status_message)
        self.send_event(source, action)
        return

      if source not in self.firefly.components:
        logging.error('[FIREBASE PUSH] ERROR: Source not in firefly components.')
        return

      if self.firefly.components[source].type == 'GROUP':
        self.db.child("homeStatus").child(self.home_id).child('groupStatus').child(source).update(action, self.id_token)
        self.send_event(source, action)
        return

      self.update_device_status(source, action)

      # TODO(zpriddy): Remove this when new UI is done.
      if 'PARAMS' in action.keys():
        return
      if 'RAW_VALUES' in action.keys():
        return
      if 'SENSORS' in action.keys():
        return
      self.db.child("homeStatus").child(self.home_id).child('devices').child(source).update(action, self.id_token)

      self.send_event(source, action)

    except Exception as e:
      logging.info('[FIREBASE PUSH] ERROR: %s' % str(e))
      self.refresh_user()
      if retry:
        self.push(source, action, False)

  def send_event(self, source, action):
    ''' add new event in the event log

    Args:
      source: ff_id of the device
      action: action to enter into event log

    Returns:

    '''
    now = self.firefly.location.now
    now_time = now.strftime("%B %d %Y %I:%M:%S %p")
    self.db.child("homeStatus").child(self.home_id).child('events').push({
      'ff_id':     source,
      'event':     action,
      'timestamp': now.timestamp(),
      'time':      now_time
    }, self.id_token)

  def push_notification(self, message, priority, retry=True):
    try:
      self.send_notification(message, priority)
    except:
      self.refresh_user()
      if retry:
        self.push_notification(message, priority, False)

  def send_notification(self, message, priority):
    now = self.firefly.location.now
    now_time = now.strftime("%B %d %Y %I:%M:%S %p")
    self.db.child("homeStatus").child(self.home_id).child('notifications').push({
      'message':   message,
      'priority':  priority,
      'timestamp': now.timestamp(),
      'time':      now_time
    }, self.id_token)

  def get_api_id(self, **kwargs):
    ff_id = kwargs.get('api_ff_id')
    callback = kwargs.get('callback')
    my_stream = None

    if ff_id is None or callback is None:
      return False

    def stream_api_key(message):
      data = message.get('data')
      if data is None:
        return

      api_key = data

      if api_key is None:
        return

      callback(firebase_api_key=api_key)
      try:
        my_stream.close()
      except:
        pass

    now = self.firefly.location.now.timestamp()
    self.db.child("homeStatus").child(self.home_id).child("apiDevices").update({
      ff_id: {
        'added': now
      }
    }, self.id_token)
    my_stream = self.db.child("homeStatus").child(self.home_id).child("apiDevices").child(ff_id).child('apiKey').stream(stream_api_key, self.id_token)


def scrub(x):
  # Converts None to empty string
  ret = copy.deepcopy(x)
  # Handle dictionaries, lits & tuples. Scrub all values
  if isinstance(x, dict):
    for k, v in ret.items():
      ret[k] = scrub(v)

  if isinstance(x, (list, tuple)):
    if isinstance(x, (tuple)):
      logging.notify(str(x))
    for k, v in enumerate(ret):
      ret[k] = scrub(v)
  # Handle None
  if x is None:
    ret = ''
  # Finished scrubbing
  return ret
