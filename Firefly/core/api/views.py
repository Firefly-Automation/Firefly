import json
import logging

from core import ffCommand, getDeviceStatusDict, getDeviceViewsList, getRoutineList
from core.firefly import app
from flask import Flask, request

@app.route('/')
def baseView():
  return "This is the root page"

@app.route('/API/core/views/routine')
def APICoreViewRoutine():
  routine_list = getRoutineList()
  return_data = {}
  for r in routine_list:
    if r.get('icon') is None:
      continue
    rID = r .get('id')
    return_data[rID] = {'id': rID, 'icon':r.get('icon')}

  logging.debug(str(return_data))
  return json.dumps(return_data, sort_keys=True)

@app.route('/API/core/views/devices')
def APICoreViewDevices():
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
def APICoreStatusDevicesAll():
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
def APICommand():
  c = dict(request.data)
  logging.critical(str(c))
  
  command = request.form.get('command')
  logging.critical(command)
  device = c.get('device')[0]
  force = c.get('force')
  routine = c.get('routine')
  source = 'web: /API/command'

  if routine:
    ffCommand(device, command, routine=routine, force=force, source=source)
  else:
    ffCommand(device, command, source=source)
  return "OK"

