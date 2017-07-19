import configparser
from difflib import get_close_matches


import pyrebase
import requests
import json
import copy

from Firefly import aliases, logging, scheduler
from Firefly.const import API_ALEXA_VIEW, API_INFO_REQUEST, SERVICE_CONFIG_FILE, TYPE_AUTOMATION, TYPE_DEVICE
from Firefly.helpers.service import Command, Request, Service
from Firefly.services.api_ai import apiai_command_reply

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
  firefly.components[SERVICE_ID] = firebase
  return True


class Firebase(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    logging.notify('setting up firebase')

    self.firefly = firefly
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
    scheduler.runEveryM(5, self.refresh_all)
    scheduler.runInS(20, self.refresh_all)
    scheduler.runEveryM(20, self.refresh_status)
    scheduler.runInS(20, self.refresh_status)

    self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.stream_handler, self.id_token)
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
    self.stream.close()
    self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.stream_handler, self.id_token)
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


  def stream_handler(self, message):
    try:
      if message['data']:
        path = message['path']
        ff_id = path[1:]
        command = message['data']
        myCommand = None
        if type(command) is str:
          myCommand = Command(ff_id, 'webapi', command)
        elif type(command) is dict:
          myCommand = Command(ff_id, 'webapi', list(command.keys())[0], **dict(list(command.values())[0]))
        self.firefly.send_command(myCommand)
        self.db.child('homeStatus').child(self.home_id).child('commands').child(ff_id).remove(self.id_token)
        if command == 'delete':
          self.refresh_all()
    except Exception as e:
      logging.notify("Firebase 153: %s" % str(e))
      self.refresh_all()
      self.db.child('homeStatus').child(self.home_id).child('commands').remove(self.id_token)

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
    all_values= all_values.replace('null', '')
    all_values = all_values.replace('#', '')
    all_values = all_values.replace('$', '')
    all_values = all_values.replace('/', '_')
    all_values = json.loads(all_values)

    try:
      alexa_views = self.get_all_alexa_views('firebase')
      self.db.child("userAlexa").child(self.uid).child("devices").set(alexa_views, self.id_token)
      routines = self.get_routines()
      # TODO DELETE ABOVE WHEN HOUSES WORK
      self.db.child("homeStatus").child(self.home_id).child('devices').update(all_values, self.id_token)
      self.db.child("homeStatus").child(self.home_id).child('routines').set(routines, self.id_token)

    except Exception as e:
      logging.notify("Firebase 177: %s" % str(e))

    self.refresh_status()

  def get_routines(self):
    routines = []
    for ff_id, d in self.firefly.components.items():
      if d.type == TYPE_AUTOMATION and 'routine' in d._package:
        routines.append({
          'alias':     d._alias,
          'title':     d._title,
          'ff_id':     ff_id,
          'icon':      d.icon,
          'mode':      d.mode,
          'export_ui': d.export_ui,
          'config':    d.export()
        })
    return routines

  def get_component_view(self, ff_id, source):
    device_request = Request(ff_id, source, API_INFO_REQUEST)
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
    # TODO MAYBE NOT RETURN HERE?
    # return views
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


  def refresh_status(self, **kwargs):
    status_data = {}
    status_data['devices'] = self.get_all_component_views('firebase_refresh', filter=TYPE_DEVICE)
    now = self.firefly.location.now
    status_data['time'] = {
      'epoch':  now.timestamp(),
      'day':    now.day,
      'month':  now.month,
      'year':   now.year,
      'hour':   now.hour,
      'minute': now.minute,
      'str':    str(now)
    }
    status_data['is_dark'] = self.firefly.location.isDark
    status_data['mode'] = self.firefly.location.mode
    status_data['last_mode'] = self.firefly.location.lastMode

    for room_alias, room in self.firefly._rooms._rooms.items():
      status_data['devices'].append({
        'ff_id': room.id,
        'alias': room.alias + ' (room)'
      })

    # Nasty json sanitation
    status_data = scrub(status_data)
    status_data = json.dumps(status_data)
    status_data = status_data.replace('null', '')
    status_data = status_data.replace('$', '')
    status_data = status_data.replace('#', '')
    status_data = status_data.replace('/', '_')
    status_data = json.loads(status_data)


    try:
      self.db.child("homeStatus").child(self.home_id).child('status').set(status_data, self.id_token)
    except Exception as e:
      logging.notify("Firebase 263: %s" % str(e))

  def refresh_user(self):
    try:
      try:
        self.stream.close()
        self.commandReplyStream.close()
      except:
        pass
      self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
      self.id_token = self.user['idToken']
      self.stream = self.db.child('homeStatus').child(self.home_id).child('commands').stream(self.stream_handler, self.id_token)
      self.commandReplyStream = self.db.child('homeStatus').child(self.home_id).child('commandReply').stream(self.command_reply, self.id_token)
    except Exception as e:
      logging.notify("Firebase 266: %s" % str(e))
      pass

  def push(self, source, action):
    try:
      self.db.child("homeStatus").child(self.home_id).child('devices').child(source).update(action, self.id_token)
      if source != 'time':
        now = self.firefly.location.now
        now_time = now.strftime("%B %d %Y %I:%M:%S")
        self.db.child("homeStatus").child(self.home_id).child('events').push({
          'ff_id':     source,
          'event':     action,
          'timestamp': now.timestamp(),
          'time':      now_time
        }, self.id_token)
    except:
      self.refresh_user()
      self.db.child("homeStatus").child(self.home_id).child('devices').child(source).update(action, self.id_token)
      if source != 'time':
        now = self.firefly.location.now
        now_time = now.strftime("%B %d %Y %I:%M:%S")
        self.db.child("homeStatus").child(self.home_id).child('events').push({
          'ff_id':     source,
          'event':     action,
          'timestamp': now.timestamp(),
          'time':      now_time
        }, self.id_token)

  def push_notification(self, message, priority):
    try:
      now = self.firefly.location.now
      now_time = now.strftime("%B %d %Y %I:%M:%S")
      self.db.child("homeStatus").child(self.home_id).child('notifications').push({
        'message':   message,
        'priority':  priority,
        'timestamp': now.timestamp(),
        'time':      now_time
      }, self.id_token)
    except:
      self.refresh_user()
      now = self.firefly.location.now
      now_time = now.strftime("%B %d %Y %I:%M:%S")
      self.db.child("homeStatus").child(self.home_id).child('notifications').push({
        'message':   message,
        'priority':  priority,
        'timestamp': now.timestamp(),
        'time':      now_time
      }, self.id_token)

  def get_api_id(self, **kwargs):
    print('^^^^^^^^^^^^^^^^^^^ GET API KEY ^^^^^^^^^^^^^^^')
    ff_id = kwargs.get('api_ff_id')
    callback = kwargs.get('callback')
    my_stream = None

    if ff_id is None or callback is None:
      return False

    def stream_api_key(message):
      data = message.get('data')
      print('*************** API_KEY: ' + str(data))
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
    self.db.child("homeStatus").child(self.home_id).child("apiDevices").update({ff_id:{'added':now}}, self.id_token)
    my_stream = self.db.child("homeStatus").child(self.home_id).child("apiDevices").child(ff_id).child('apiKey').stream(stream_api_key, self.id_token)




def scrub(x):
  # Converts None to empty string
  ret = copy.deepcopy(x)
  # Handle dictionaries, lits & tuples. Scrub all values
  if isinstance(x, dict):
    for k, v in ret.items():
      ret[k] = scrub(v)

  if isinstance(x, (list, tuple)):
    for k, v in enumerate(ret):
      ret[k] = scrub(v)
  # Handle None
  if x is None:
    ret = ''
  # Finished scrubbing
  return ret