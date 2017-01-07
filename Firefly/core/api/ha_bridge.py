# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-12-24 12:39:45
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-12-24 20:34:28

import difflib
import json
import logging
import requests

from core import ffCommand
from core.database.device_db import getDeviceList
from core.database.routine_db import getRoutineList
from core.database.device_db import getDeviceInfo
from core import configPath
import os

# TODO: Pull this info from the firefly.confg 
FIREFLY_ADDRESS = 'http://localhost:6002'
HA_BRIDGE_ADDRESS = 'http://localhost:80/api/devices'


def ha_bridge_handler(p_request):
  action = p_request.get('action')
  if action == 'dim':
    return ha_bridge_dim(p_request)
  elif action == 'on':
    return ha_bridge_on(p_request)
  elif action == 'off':
    return ha_bridge_off(p_request)
  else:
    return ""

def ha_bridge_dim(p_request):
  ffCommand(p_request.get('device'), {'setLight' : {'level':p_request.get('level')}}, source='HA Bridge')
  return ""

def ha_bridge_on(p_request):
  ffCommand(p_request.get('device'), {'switch': 'on'}, source='HA Bridge')
  return ""

def ha_bridge_off(p_request):
  ffCommand(p_request.get('device'), {'switch': 'off'}, source='HA Bridge')
  return ""

def ha_bridge_push_config():
  # 1) Get the HA-Bridge config details from request.
  # 2) Build of the URLS and JSON for each device and push them.
  # 3) Delete existing Firefly Configs
  # 4) Add the devices to the HA-Bridge

  devices = getDeviceInfo(filters=['lights','light','switch','hue','dimmer','fan','group'])


  device_config = []

  # TODO make this read the ha-bridge config fiel
  ha_bride_alias = {}
  with open(os.path.join(configPath,'ha_bridge_alias.json')) as alias:
    ha_bride_alias = json.load(alias)
    
  
  for device, config in devices.iteritems(): 
    d_config = {
      'name': config.get('name'),
      'deviceType': config.get('type'),
      'onUrl': FIREFLY_ADDRESS + '/API/habridge/command',
      'offUrl': FIREFLY_ADDRESS + '/API/habridge/command',
      'dimUrl': FIREFLY_ADDRESS + '/API/habridge/command',
      'targetDevice': 'Firefly - Auto-added',
      'httpVerb': 'POST',
      'contentType': 'application/json',
      'contentBody': '{"device": "' + config.get('id') + '" ,"action": "on"}',
      'contentBodyOff': '{"device": "' + config.get('id') + '" ,"action": "off"}',
      'contentBodyDim': '{"device": "' + config.get('id') + '" ,"action": "dim", "level":${intensity.percent}}'
    }
    if ha_bride_alias.get(d_config.get('name')):
      d_config['name'] = ha_bride_alias['name']
    device_config.append(d_config)

  current_devices = requests.get(HA_BRIDGE_ADDRESS).json()
  for d in current_devices:
    if d.get('targetDevice') == 'Firefly - Auto-added':
      requests.delete(HA_BRIDGE_ADDRESS + '/' + str(d.get('id')))


  for d in device_config:
    r = requests.post(HA_BRIDGE_ADDRESS, json=d)
    logging.critical('Added ' + d.get('name') + ' to HA Bridge')

  logging.critical('Done addeding devices to HA Bridge.')

  return str(device_config)


