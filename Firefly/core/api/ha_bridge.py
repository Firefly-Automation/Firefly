# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-12-24 12:39:45
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-12-24 17:35:55

import difflib
import json
import logging
import requests

from core import ffCommand
from core.database.device_db import getDeviceList
from core.database.routine_db import getRoutineList
from core.database.device_db import getDeviceInfo

FIREFLY_ADDRESS = 'http://localhost:6002'
HA_BRIDGE_ADDRESS = 'http://localhost:80'


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
	# 3) Add the devices to the HA-Bridge

	devices = getDeviceInfo(filters=['lights','light','switch','hue','dimmer','fan','group'])


	device_config = []
	
	for device, config in devices.iteritems(): 
		d_config = {
			'name': config.get('name'),
			'deviceType': config.get('type'),
			'onUrl': FIREFLY_ADDRESS + '/API/habridge/command',
			'offUrl': FIREFLY_ADDRESS + '/API/habridge/command',
			'dimUrl': FIREFLY_ADDRESS + '/API/habridge/command',
			'httpVerb': 'POST',
			'contentType': 'application/json',
			'contentBody': {
				'device': config.get('id'),
				'action': 'on'
			},
			'contentBodyOff': {
				'device': config.get('id'),
				'action': 'off'
			},
			'contentBodyDim': {
				'device': config.get('id'),
				'action': 'dim',
				'level': '${intensity.percent}'
			}
		}
		device_config.append(d_config)


	for d in device_config:
		r = requests.post(HA_BRIDGE_ADDRESS, json=d)
		logging.critical('Added ' + d.get('name') + ' to HA Bridge')

	logging.critical('Done addeding devices to HA Bridge.')

	return str(device_config)



