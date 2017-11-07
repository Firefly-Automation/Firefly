import configparser
from time import sleep

import requests
import aiohttp

from Firefly import logging, scheduler
from Firefly.const import COMMAND_UPDATE, SERVICE_CONFIG_FILE
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

from Firefly.core.service_handler import ServicePackage, ServiceConfig

TITLE = 'Hue service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_hue'
COMMANDS = ['send_command', 'refresh', 'send_request']
REQUESTS = ['get_lights', 'get_groups', 'get_orphans']

SECTION = 'HUE'


def Setup(firefly, package, alias, ff_id, service_package:ServicePackage, config:ServiceConfig, **kwargs):
  logging.info('Setting up %s service' % service_package.name)
  hue = Hue(firefly, alias, ff_id, service_package, config, **kwargs)
  firefly.install_component(hue)
  return True


class Hue(Service):
  def __init__(self, firefly, alias, ff_id, service_package:ServicePackage, config:ServiceConfig, **kwargs):
    #TODO: Fix this
    package = service_package.package
    super().__init__(firefly, ff_id, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self.config = config
    self._ip = config.ip
    self._username = config.username
    self._enable = config.enabled

    self._installed_items = {}

    self.add_command('send_request', self.send_request)
    # self.add_command('refresh', self.refresh)

    # self.add_request('get_lights', self.get_lights)
    # self.add_request('get_groups', self.get_groups)
    # self.add_request('get_orphans', self.get_orphans)

    self._rCount = 0

    self.temp_disabled = False
    self._request_count = 0

    self.initialize_hue()
    scheduler.runEveryS(10, self.refresh)
    scheduler.runInM(5, self.reset_request_count)


  def initialize_hue(self, **kwargs):
    if not self._ip:
      self.get_ip()
    if not self._username:
      self.register()


  def reset_request_count(self):
    logging.info('resetting request count.')
    self._request_count = 0

  def temp_disable(self, disable_min):
    logging.info("Disabling hue for %d min" % disable_min)
    self.reset_request_count()
    self.temp_disabled = True
    scheduler.runInM(disable_min, self.end_temp_disable)

  def end_temp_disable(self):
    logging.info("Re-Enabling Hue")
    self.temp_disabled = False

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
    """

    Args:
      path: (str) url path
      data: (dict) json data to post
      method: (str) HTTP Method [GET POST PUT]
      return_json: (bool) return the json data requested otherwise the request object is returned
      no_username: (bool) is there a username provided, no_username is used for initial pairing
      **kwargs:

    Returns:
      if None is returned then there was an error making the request.
      You should be able to handle None, Request Response or JSON dict with your function.
      if return_json is passed then only the JSON output is returned, otherwise the full request object is returned.

    """
    if self.temp_disabled:
      return None

    r = None
    url = ''
    if (no_username or not self._username):
      url = 'http://%s/%s' % (self._ip, path)
    elif path is None:
      url = 'http://%s/api/%s/' % (self._ip, self._username)
    else:
      url = 'http://%s/api/%s/%s' % (self._ip, self._username, path)

    try:
      if method == 'POST':
        r = requests.post(url, json=data)

      elif method == 'PUT':
        r = requests.put(url, json=data)
        logging.error("[HUE] send_request is deprecated for PUT method requests")

      elif method == 'GET':
        if data:
          r = requests.get(url, json=data)
        else:
          r = requests.get(url)
    except requests.RequestException as e:
      logging.error(code='FF.HUE.SEN.005')  # request time out
      self._request_count += 1
      if self._request_count > 5:
        self.temp_disable(1)
    except Exception as e:
      logging.error(code='FF.HUE.SEN.006')  # unknown hue error

    if return_json and r is not None:
      return r.json()
    return r

  def register(self):
    request_data = {
      'devicetype': 'firefly'
    }
    response = self.send_request('api', request_data, method='POST', no_username=True)[0]
    if response is None:
      logging.error(code='FF.HUE.REG.001')  # error talking to hue bridge

    logging.debug('Response: ' + str(response))

    if 'error' in response:
      if response['error']['type'] == 101:
        if self._rCount % 5 == 0 or self._rCount == 0:
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
      self.config.ip = self._ip
      self.config.username = self._username
      self.config.save()
      logging.info('Config file for hue has been updated.')


  #TODO: Rename this when more functionality is added.
  async def makeHuePutRequest(self, url, data, method):
    async with aiohttp.ClientSession() as session:
      if method == 'PUT':
        async with session.put(url, data=data, timeout=10) as resp:
          return await resp.status == 200


  def sendLightRequest(self, request):
    if 'lightID' in request.keys():
      logging.debug('Sending Light Request')
      #success = self.send_request('lights/' + str(request.get('lightID')) + '/state', data=request.get('data'), method='PUT')
      success = self.makeHuePutRequest('lights/' + str(request.get('lightID')) + '/state', data=request.get('data'), method='PUT')
      if success is None:
        logging.error(code='FF.HUE.SEN.001')  # error talking to hue bridge
      return
    logging.error(code='FF.HUE.SEN.003')  # no light id given


  def sendGroupRequest(self, request):
    if 'groupID' in request.keys():
      logging.debug('Sending Group Request')
      #success = self.send_request('groups/' + str(request.get('groupID')) + '/action', data=request.get('data'), method='PUT')
      success = self.makeHuePutRequest('groups/' + str(request.get('groupID')) + '/action', data=request.get('data'), method='PUT')
      if success is None:
        logging.error(code='FF.HUE.SEN.002')  # error talking to hue bridge
      return
    logging.error(code='FF.HUE.SEN.004')  # no group id given

  def refresh(self):
    #TODO: Make this an async function with a callback when data is gathered.
    data = self.send_request()
    # TODO: Handle errors like:
    # [{'error': {'type': 1, 'address': '/', 'description': 'unauthorized user'}}] that is returned as data

    if data is None:
      logging.error(code='FF.HUE.REF.001')  # error talking to hue hub
      return

    need_to_refresh = False

    for light_id, light in data['lights'].items():
      ff_id = light['uniqueid']
      light['hue_number'] = light_id
      light['hue_service'] = SERVICE_ID

      if ff_id in self._firefly.components:
        command = Command(ff_id, SERVICE_ID, COMMAND_UPDATE, **light)
        self._firefly.send_command(command)
      else:
        self._firefly.install_package('Firefly.components.hue.hue_light', ff_id=ff_id, alias=light.get('name'), **light)
        need_to_refresh = True

    for group_id, group in data['groups'].items():
      ff_id = 'hue-group-device-%s' % str(group_id)
      group['hue_number'] = group_id
      group['hue_service'] = SERVICE_ID

      if ff_id in self._firefly.components:
        command = Command(ff_id, SERVICE_ID, COMMAND_UPDATE, **group)
        self._firefly.send_command(command)
      else:
        self._firefly.install_package('Firefly.components.hue.hue_group', ff_id=ff_id, alias=group.get('name'), **group)
        need_to_refresh = True

    if need_to_refresh:
      self.refresh_firebase()

  def refresh_firebase(self):
    refresh_command = Command('service_firebase', 'hue', 'refresh')
    self._firefly.send_command(refresh_command)
