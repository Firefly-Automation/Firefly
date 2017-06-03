import configparser

import pyrebase

from Firefly import logging
from Firefly.const import SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service, Request, Command
from Firefly import scheduler
from Firefly.const import TYPE_DEVICE,API_INFO_REQUEST, API_ALEXA_VIEW



TITLE = 'Firebase Service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_firebase'
COMMANDS = ['push']
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
  if api_key is None:
    logging.error('firebase error')  # TODO Make this error code
    return False
  firebase = Firebase(firefly, package, api_key=api_key, auth_domain=auth_domain, database_url=database_url,
                      email=email, password=password, storage_bucket=storage_bucket)
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

    self.add_command('push', self.push)

    self.config = {
      "apiKey":      self.api_key,
      "authDomain":  self.auth_domain,
      "databaseURL": self.database_url,
      "storageBucket" : self.storage_bucket
    }


    self.firebase = pyrebase.initialize_app(self.config)

    # Get a reference to the auth service
    self.auth = self.firebase.auth()


    # Log the user in
    self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
    self.uid = self.user['localId']
    self.id_token = self.user['idToken']

    print('***********************')
    print(str(self.user))
    print('***********************')


    # Get a reference to the database service
    self.db = self.firebase.database()

    scheduler.runEveryM(30, self.refresh_user)
    scheduler.runEveryM(5, self.refresh_all)
    scheduler.runInS(20, self.refresh_all)
    scheduler.runEveryM(20, self.refresh_status)
    scheduler.runInS(20, self.refresh_status)

    self.stream = self.db.child("userCommands").child(self.uid).stream(self.stream_handler, self.id_token)


  def refresh_stream(self):
    self.stream.close()
    self.stream = self.db.child("userCommands").child(self.uid).stream(self.stream_handler, self.id_token)

  def stream_handler(self, message):
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

      self.db.child("userCommands/" + self.uid).child(ff_id).remove(self.id_token)



  def refresh_all(self):
    # Hard-coded refresh all device values
    # TODO use core api for this.
    all_values = {}
    for ff_id, device in self.firefly.components.items():
      try:
        all_values[ff_id] = device.get_all_request_values()
      except:
        pass

    try:
      self.db.child("userDevices").child(self.uid).update(all_values, self.id_token)

      alexa_views = self.get_all_alexa_views('firebase')
      self.db.child("userAlexa").child(self.uid).child("devices").set(alexa_views, self.id_token)

      modes = self.firefly.location.modes
      self.db.child("userModes").child(self.uid).set(modes, self.id_token)
    except Exception as e:
      logging.notify(e)


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
        data =  self.get_component_view(ff_id, source)
        views.append(data)
    return views


  def refresh_status(self):
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
    print(status_data)

    try:
      self.db.child("userStatus").child(self.uid).set(status_data, self.id_token)
    except Exception as e:
      logging.notify(e)


  def refresh_user(self):
    #TODO FIX THIS
    #self.user = self.auth.refresh(self.user['refreshToken'])
    #self.id_token = self.user['idToken']

    #self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
    #self.uid = self.user['localId']
    #self.id_token = self.user['idToken']

    #self.stream.close()
    #self.stream = self.db.child("userCommands").child(self.uid).stream(self.stream_handler, self.id_token)
    try:
      try:
        self.stream.close()
      except:
        pass
      self.user = self.auth.refresh(self.user['refreshToken'])
      self.id_token = self.user['idToken']
      self.stream = self.db.child("userCommands").child(self.uid).stream(self.stream_handler, self.id_token)
      #logging.notify('Token Refreshed')
    except Exception as e:
      #logging.notify(e)
      try:
        try:
          self.stream.close()
        except:
          pass
        self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
        self.id_token = self.user['idToken']
        self.stream = self.db.child("userCommands").child(self.uid).stream(self.stream_handler, self.id_token)
      except Exception as e:
        #logging.notify('failed to reauth for stream')
        #logging.notify(e)
        pass


  def push(self, source, action):
    self.db.child("userDevices").child(self.uid).child(source).update(action, self.id_token)


