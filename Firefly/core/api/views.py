import json
import logging

from core import ffCommand
from core import ffLocation
from core import getDeviceStatusDict
from core import getDeviceViewsList
from core import getRoutineViewsDict
from core import reinstallRoutinesFromConfig
from core.api.alexa import alexaHandler
from core.api.ifttt import iftttHandler
from core.api.locative import locativeHandler
from core.api.ha_bridge import ha_bridge_handler
from core.api.ha_bridge import ha_bridge_push_config
from core.firefly import app
from flask import request

#FIX
from core.database.device_db import reinstallDevices
from core.database.device_db import reinstall_indigo

from core.database.device_db import DeviceViews

device_views = DeviceViews()


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

@app.route('/API/habridge/command', methods=['POST'])
def ha_bridge_command():
  r = request.get_json(force=True)
  return ha_bridge_handler(r)

@app.route('/API/habridge/config', methods=['POST','GET'])
def ha_bridge_config():
  return ha_bridge_push_config()

@app.route('/API/mode')
def apiMode():
  return ffLocation.mode


@app.route('/support/reinstall_routines')
def supportRinstallRoutines():
  config_file = '/opt/firefly_syste/config/routine.json'
  reinstallRoutinesFromConfig(config_file)
  return 'Routines Reinstalled'


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
  #devices = getDeviceViewsList()
  devices = device_views.deviceViewsList
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
  device_status = device_views.deviceStatusDict
  #device_status = getDeviceStatusDict()
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
  # Refresh device views on change on UI
  device_views.refreshViews()
  return "OK"


#rough hacks.. Fix soon

@app.route('/support/reinstall_devices')
def apiReinstallDevices():
  reinstallDevices()
  return "OK"

@app.route('/support/reinstall_indigo')
def apiSupportReinstallIndigo():
  reinstall_indigo()
  return "OK"

@app.route('/reinstall_apps')
def apiReinstallApps():
  from core import appsDB
  from sys import modules
  from collections import OrderedDict
  import pickle
  appsDB.remove({})
  with open('config/apps.json') as coreAppConfig:
    appList = json.load(coreAppConfig)
    for packageName, module in appList.iteritems():
      for moduleName in module:
        package_full_path = 'apps.' + str(packageName) + '.' + str(moduleName)
        app_package_config = 'config/app_config/' + str(packageName) + '/config.json'
        logging.critical(app_package_config)
        with open(str(app_package_config)) as app_package_config_file:
          app_package_config_data = json.load(app_package_config_file, object_pairs_hook=OrderedDict).get(moduleName) #json.load(app_package_config_file).get(moduleName)
          logging.critical(app_package_config_data)
          package = __import__(package_full_path, globals={}, locals={}, fromlist=[str(packageName)], level=-1)
          reload(modules[package_full_path])
          for install in app_package_config_data.get('installs'):
            aObj = package.App(install)
            aObjBin = pickle.dumps(aObj)
            a = {}
            a['id'] = aObj.id
            a['ffObject'] = aObjBin
            a['name'] = install.get('name')
            a['listen'] = aObj.listen
            appsDB.insert(a)
  return "OK"
