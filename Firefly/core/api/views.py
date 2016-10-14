import json
import logging

from core import ffCommand
from core import ffLocation
from core import getDeviceStatusDict
from core import getDeviceViewsList
from core import getRoutineViewsDict
from core.api.alexa import alexaHandler
from core.api.ifttt import iftttHandler
from core.api.locative import locativeHandler
from core.firefly import app
from flask import request


@app.route('/')
def baseView():
  return "This is the root page"


@app.route('/API/alexa', methods=['POST'])
def apiAlexa():
  r = request.get_json(force=True)
  return alexaHandler(r)


@app.route('/API/ifttt', methods=['POST'])
def apiIFTTT():
  r = request.get_json(force=True)
  return iftttHandler(r)


@app.route('/API/locative', methods=['POST'])
def locativeAPI():
  locativeHandler(request)
  return str(True)


@app.route('/API/mode')
def apiMode():
  return ffLocation.mode


@app.route('/API/core/views/routine')
def apiCoreViewRoutine():
  routine_list = getRoutineViewsDict()
  return_data = {}
  for r in routine_list:
    if r.get('icon') is None:
      continue
    rID = r .get('id')
    return_data[rID] = {'id': rID, 'icon': r.get('icon')}

  logging.debug(str(return_data))
  return json.dumps(return_data, sort_keys=True)


@app.route('/API/core/views/devices')
def apiCoreViewDevices():
  devices = getDeviceViewsList()
  return_data = {'devices': devices}

  device_type_list = []
  for d in devices:
    d_type = d.get('type')
    if d_type not in device_type_list:
      device_type_list.append(d_type)

  device_types = [
      {
          'index': 0,
          'type': 'all',
          'title': 'all devices'
      }
  ]

  device_index = 1
  for d in sorted(device_type_list):
    device_types.append({
        'index': device_index,
        'type': str(d),
        'title': str(d)
    })
    device_index += 1

  return_data['types'] = device_types

  return json.dumps(return_data, sort_keys=True)


@app.route('/API/core/status/devices/all')
def apiCoreStatusDevicesAll():
  device_status = getDeviceStatusDict()
  return_data = {'devices': device_status}

  device_type_list = []
  for name, d in device_status.iteritems():
    if d.get('views'):
      d_type = d.get('views').get('type')
      if d_type not in device_type_list:
        device_type_list.append(d_type)

  device_types = [
      {
          'index': 0,
          'type': 'all',
          'title': 'all devices'
      }
  ]

  device_index = 1
  for d in sorted(device_type_list):
    device_types.append({
        'index': device_index,
        'type': str(d),
        'title': str(d)
    })
    device_index += 1
  return_data['types'] = device_types
  return json.dumps(return_data, sort_keys=True)


@app.route('/API/command', methods=['POST'])
def apiCommand():
  c = request.get_json(force=True)
  logging.critical(str(c))

  command = c.get('command')
  logging.critical(command)
  device = c.get('device')
  force = c.get('force')
  routine = c.get('routine')
  source = 'web: /API/command'

  if routine:
    ffCommand(device, command, routine=routine, force=force, source=source)
  else:
    ffCommand(device, command, source=source)
  return "OK"
