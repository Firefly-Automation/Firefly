import configparser
from Firefly import scheduler
from Firefly import logging
from Firefly.const import SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service
from Firefly.helpers.events import Command
import requests
import json
import asyncio
from Firefly.const import COMMAND_UPDATE
from time import sleep
from Firefly.components.hue import hue_light

TITLE = 'Hue service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_hue'
COMMANDS = ['send_command', 'refresh', 'send_request']
REQUESTS = ['get_lights', 'get_groups', 'get_orphans']

SECTION = 'HUE'


def Setup(firefly, package, **kwargs):
  logging.message('Setting up %s service' % SERVICE_ID)
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)

  enable = config.getboolean(SECTION, 'enable', fallback=False)
  ip = config.get(SECTION, 'ip', fallback=None)
  username = config.get(SECTION, 'username', fallback=None)

  hue = Hue(firefly, package, enable=enable, ip=ip, username=username,  **kwargs)
  firefly.components[SERVICE_ID] = hue

  if not enable:
    return False
  return True


class Hue(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self._ip = kwargs.get('ip')
    self._username = kwargs.get('username')
    self._enable = kwargs.get('enable')

    self._installed_items = {}

    self.add_command('send_request', self.send_request)
    #self.add_command('refresh', self.refresh)

    #self.add_request('get_lights', self.get_lights)
    #self.add_request('get_groups', self.get_groups)
    #self.add_request('get_orphans', self.get_orphans)

    self._rCount = 0
    print(self._ip)

    self.initialize_hue()
    scheduler.runEveryS(10, self.refresh)

  def initialize_hue(self, **kwargs):
    if not self._ip:
      self.get_ip()
    if not self._username:
      self.register()


  def get_ip(self):
    data = requests.get('http://www.meethue.com/api/nupnp')
    try:
      self._ip = data.json()[0]['internalipaddress']
    except:
      logging.error(code='FF.HUE.GET.001')  # problem parsing ip address of bridge
      self._enable = False
    if not self._ip:
      logging.error(code='FF.HUE.GET.002')  # problem parsing ip address of bridge
      self._enable = False

  def send_request(self, path=None, data=None, method='GET', return_json=True, no_username=False, **kwargs):
    if data:
      data = json.dumps(data)

    r = None
    url = ''
    if (no_username or not self._username):
      url = 'http://%s/%s' % (self._ip, path)
    elif path is None:
      url = 'http://%s/api/%s/' % (self._ip, self._username)
    else:
      url = 'http://%s/api/%s/%s' % (self._ip, self._username, path)

    logging.debug('Request URL: ' + url + ' Method: ' + method)

    if method == 'POST':
      r = requests.post(url, data=data)

    elif method == 'PUT':
      r = requests.put(url, data=data)

    elif method == 'GET':
      if data:
        r = requests.get(url, data=data)
      else:
        r = requests.get(url)

    if return_json and r is not None:
      return r.json()
    return r

  def register(self):
    request_data = {'devicetype': 'firefly'}
    response = self.send_request('api', request_data, method='POST', no_username=True)[0]

    logging.debug('Response: ' + str(response))

    if 'error' in response:
      if response['error']['type'] == 101:
        if self._rCount%5 == 0 or self._rCount == 0:
          logging.notify('Please press the hue button.')
        if (self._rCount < 30):
          sleep(10)
          self.register()
          self._rCount += 1
        else:
          logging.notify('Hue button was not pressed. Disabling Hue.')

    if 'success' in response:
      self._username = response['success']['username']
      logging.debug('Success! username: %s' % str(self._username))

      config = configparser.ConfigParser()
      config.read(SERVICE_CONFIG_FILE)
      config.set(SECTION, r'username', str(self._username))
      config.set(SECTION, r'ip', str(self._ip))
      with open(SERVICE_CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
      logging.info('Config file for hue has been updated.')

  def sendLightRequest(self, request):
    if 'lightID' in request.keys():
      logging.debug('Sending Light Request')
      self.send_request('lights/' + str(request.get('lightID')) + '/state', data=request.get('data'), method='PUT')


  def sendGroupRequest(self, request):
    if 'groupID' in request.keys():
      logging.debug('Sending Group Request')
      self.send_request('groups/' + str(request.get('groupID')) + '/action', data=request.get('data'), method='PUT')


  def refresh(self):
    data = self.send_request()

    for light_id, light in data['lights'].items():
      ff_id = light['uniqueid']
      light['hue_number'] = light_id
      light['hue_service'] = SERVICE_ID

      if ff_id in self._firefly.components:
        command = Command(ff_id, SERVICE_ID,COMMAND_UPDATE, **light)
        self._firefly.send_command(command)
      else:
        self._firefly.install_package('Firefly.components.hue.hue_light', ff_id=ff_id, alias=light.get('name'), **light)


    for group_id, group in data['groups'].items():
      ff_id = 'hue-group-device-%s' % str(group_id)
      group['hue_number'] = group_id
      group['hue_service'] = SERVICE_ID

      if ff_id in self._firefly.components:
        command = Command(ff_id, SERVICE_ID,COMMAND_UPDATE, **group)
        self._firefly.send_command(command)
      else:
        self._firefly.install_package('Firefly.components.hue.hue_group', ff_id=ff_id, alias=group.get('name'), **group)






