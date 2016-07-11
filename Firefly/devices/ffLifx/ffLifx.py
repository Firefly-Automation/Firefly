# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-03 08:06:32
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-26 22:59:44
import ffLifx_light as lightDevice
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent
from math import ceil

import requests
import treq

PRESETS_CT = {
  'cloudy' : '6500K',
  'daylight' : '6000K',
  'noon' : '5200K',
  'sunny' : '5500K',
  'candle' : '2000K',
  'soft white' : '2700K',
  'warm white' : '3000K',
  'halogen' : '3200K',
  'fluorescent' : '4500K',
  'incandescent' : '2800K',
}

class Device(Device):
  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly LIFX Controller',
      'type' : 'hub',
      'package' : 'ffLifx',
      'module' : 'ffLifx'
    }

    self.COMMANDS = {
      'install' : self.install_lifx,
      'sendLightCommand' : self.sendLightCommand,
      'sendMulti' : self.sendMulti,
      'sendAll' : self.sendAll,
      'update' : self.update
    }

    self.REQUESTS = {

    }

    self.VIEWS = {}

    args = args.get('args')
    self._api_key = args.get('api_key')
    self._api_url = 'https://api.lifx.com/v1/lights/'

    name = args.get('name')
    super(Device,self).__init__(deviceID, name)

    self.install_lifx()

  def install_lifx(self, args={}):
    from core.firefly_api import install_child_device
    lightData = self.getLights()
    for light, data in lightData['lights'].iteritems():
      data['bridgeID'] = self._id
      data['args'] = data
      data['args']['name'] = data.get('label')
      newLight = lightDevice.Device(light, data)
      lData = {}
      lData['name'] = data.get('label')
      lData['args'] = {'name':data.get('label')}
      install_child_device(light, newLight, config=lData)

  def sendAll(self, args={}):
    logging.critical('Setting All Lights')

    data = args.get('lightCommand')

    url = self._api_url + 'all/state'
    treq.put(url, headers=self.header, data=data)
    #if r.status_code == 200:
    return True
    #return False

  def sendLightCommand(self, args={}):
    logging.critical(args)
    data = args.get('lightCommand')
    url = self._api_url + 'id:' + str(args.get('lightID')) + '/state'
    treq.put(url, headers=self.header, data=data)
    return True


  def sendMulti(self, args={}):
    pass
    #TODO: Create a way to set multiple lights at once

  def getLights(self, args={}):
    url = self._api_url + 'all'

    r = requests.get(url, headers=self.header)
    lightsData =  r.json()

    lights = {}
    groups = []

    for light in lightsData:
      lights[light.get('uuid')] = light
      if light.get('group'):
        if light.get('group').get('id') not in groups:
          groups.append(light.get('group').get('id'))

    return {'lights':lights, 'groups':groups}


  def update(self, **kwargs):
    pass


  @property
  def header(self):
    return {'Authorization' : 'Bearer ' + self._api_key}

