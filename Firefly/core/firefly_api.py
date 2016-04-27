# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 08:56:32
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-26 22:31:26
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import OrderedDict
from datetime import datetime
import json
import logging
from klein import Klein
import treq
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python import log
from bson.binary import Binary
import pickle
import pymongo
from pymongo import MongoClient
from sys import modules

import templates

from core.models import core_settings, event

from core.models.event import Event as ffEvent
from core.models.command import Command as ffCommand
from core.models.request import Request as ffRequest
from core.location import Location
from core.scheduler import Scheduler

app = Klein()
core_settings = core_settings.Settings()

## Monogo Setup ##
client = MongoClient()
ffDB = client.ff
routineDB = ffDB.routines
deviceDB = ffDB.devices
datalogDB = ffDB.datalog
messageDB = ffDB.message
appsDB = ffDB.apps

datalogDB.ensure_index("timestamp", expireAfterSeconds=(60*60*72))
messageDB.ensure_index("timestamp", expireAfterSeconds=(60*60*24*7))



testDevices = {}
ffLocation = Location('config/location.json')
ffScheduler = Scheduler()
ffZwave = None

## PATHS ##
@app.route('/')
def pg_root(request):
  log.msg('hello world')
  return 'I am the root page!'

@app.route('/manual_command', methods=['GET','POST'])
def manual_command(request):
  device_names = {}
  for d in deviceDB.find({},{"config.name":1,"id":1}):
    device_names[d.get('config').get('name')] = d.get('id')
  
  device_list = ''
  for name, did in device_names.iteritems():
    device_list += str(name) + '  -  ' + str(did) + '<br>'

  form = '''
    <html>
    <h1>Manual Command</h1>
    <br>
    <form action="manual_command" method="POST" id="command">
    <textarea form ="command" name="myCommand" id="myCommand" rows="6" cols="70" wrap="soft"></textarea>
    <input type="submit">
    </form>
    Sample Commands <br>
    <a href='?myCommand={"device":"hue-light-8", "command":{"switch":"on"}}'>{"device":"hue-light-8", "command":{"switch":"on"}}</a> <br>
    <a href='?myCommand={"device":"hue-light-8", "command":{"switch":"off"}}'>{"device":"hue-light-8", "command":{"switch":"off"}}</a> <br>
    <a href='?myCommand={"device":"ZachPushover", "command":{"notify":{"message":"New Test Message"}}}'>{"device":"ZachPushover", "command":{"notify":{"message":"New Test Message"}}}</a> <br>
    <a href='?myCommand={"device":"Zach Presence", "command":{"presence":true}}'>{"device":"Zach Presence", "command":{"presence":true}}</a> <br>
    <a href='?myCommand={"device":"Zach Presence", "command":{"presence":false}}'>{"device":"Zach Presence", "command":{"presence":false}}</a> <br>
    <a href='?myCommand={"device":"hue-group-4", "command":{"setLight":{"preset":"cloudy", "transitiontime":40,"effect":"none","level":100,"alert":"lselect"}}}'>{"device":"hue-group-4", "command":{"setLight":{"preset":"cloudy", "transitiontime":40,"effect":"none","level":100,"alert":"lselect"}}}</a> <br>
    <br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"setLight":{"effect":"colorloop","level":50}}}'>{"device":"hue-light-3", "command":{"setLight":{"effect":"colorloop","level":50}}}</a><br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"setLight":{"effect":"none","level":50}}}'>{"device":"hue-light-3", "command":{"setLight":{"effect":"none","level":50}}}</a><br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"switch":"on"}}'>{"device":"hue-light-3", "command":{"switch":"on"}}</a> <br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"switch":"off"}}'>{"device":"hue-light-3", "command":{"switch":"off"}}</a> <br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"setLight":{"name":"red","level":100}}}'>{"device":"hue-light-3", "command":{"setLight":{"name":"red","level":100}}}</a><br>
    <a href='?myCommand={"device":"hue-light-3", "command":{"setLight":{"name":"blue","level":100}}}'>{"device":"hue-light-3", "command":{"setLight":{"name":"blue","level":100}}}</a><br>
    <a href='?myCommand={"device":"hue-group-4", "command":{"ctfade":{"startK":6500, "endK":2700, "fadeS":900}}}'>{"device":"hue-group-4", "command":{"ctfade":{"startK":6500, "endK":2700, "fadeS":900}}}</a>

    <br>
    <br>
    <a href='?myCommand={"device":"home","routine":true, "force":true}'>{"device":"home","routine":true, "force":true}</a> <br>
    <a href='?myCommand={"device":"night","routine":true, "force":true}'>{"device":"night","routine":true, "force":true}</a> <br>
    <a href='?myCommand={"device":"away","routine":true, "force":true}'>{"device":"away","routine":true, "force":true}</a> <br>
    <a href='?myCommand={"device":"sexy","routine":true, "force":true}'>{"device":"sexy","routine":true, "force":true}</a> <br>
    <a href='?myCommand={"device":"morning","routine":true, "force":true}'>{"device":"morning","routine":true, "force":true}</a> <br>
    <a href='?myCommand={"device":"sunset","routine":true, "force":true}'>{"device":"sunset","routine":true, "force":true}</a> <br>
    <br>
    <a href="http://www.w3schools.com/colors/colors_hex.asp"> Color Names </a><br>
    <br>
    Devices:<br>''' + device_list + '''
    </html>
    '''
  if request.method == 'POST' or request.args.get('myCommand'):
    try:
      command = json.loads(request.args.get('myCommand')[0])
      if command.get('routine'):
        myCommand = ffCommand(command.get('device'),command.get('command'), routine=command.get('routine'), force=command.get('force'), source='Web: Manual Command').result
      else:
        myCommand = ffCommand(command.get('device'),command.get('command'), source='Web: Manual Command').result
      return form + '<br><br> Last Command: ' + str(request.args.get('myCommand')[0])  + 'Sucessfully sent to device: ' + str(myCommand)
    except ValueError:
      return form + '<br><br>Last Command Failed - INVALID JSON FORMAT ' + str(request.args.get('myCommand')[0])
  else:
    return form + str(request.args)

@app.route('/API/control', methods=['POST'])
def api_control(request):
  request.setHeader('Content-Type', 'application/json')
  body = json.loads(request.content.read())
  device =  body.get('device')
  command = body.get('command')
  result = ffCommand(device,command)
  return json.dumps({'action':'recieved'})

@app.route('/readConfig')
def ff_read_device_config(request):
  from core.models import routine
  

  #Remove Existing Routines
  routineDB.remove({})
  with open('config/routine.json') as routines:
    testRoutines = json.load(routines, object_pairs_hook=OrderedDict)
    for r in testRoutines.get('routines'):
      rObj = routine.Routine(json.dumps(r))
      rObjBin = pickle.dumps(rObj)
      r['listen'] = rObj.listen
      r['ffObject'] = rObjBin
      routineDB.insert(r)

@app.route('/installApps')
def ff_instal_apps(request):
  appsDB.remove({})
  with open('config/apps.json') as coreAppConfig:
    appList = json.load(coreAppConfig)
    for name, app in appList.iteritems():
      package_full_path = 'apps.' + app.get('package') +'.' + app.get('module')
      app_config = 'config/app_config/' + str(name) + '.json'
      with open(str(app_config)) as app_config_file:
        app_config_data = json.load(app_config_file)
        package = __import__(package_full_path, globals={}, locals={}, fromlist=[app.get('package')], level=-1)
        reload(modules[package_full_path])
        aObj = package.App(app_config_data)
        aObjBin = pickle.dumps(aObj)
        a = {}
        a['id'] = aObj.id
        a['ffObject'] = aObjBin
        a['name'] = name
        a['listen'] = aObj.listen
        appsDB.insert(a)


@app.route('/testRequest')
def send_test_request(request):
  ffEvent('location',{'time':'sunset'})
  return 'EVENT SENT'

@app.route('/testInstall')
def test_install(request):
  global ffZwave
  deviceDB.remove({})
  with open('config/devices.json') as devices:
    allDevices = json.load(devices)
    for name, device in allDevices.iteritems():
      if device.get('module') != "ffZwave":
        package_full_path = device.get('type') + 's.' + device.get('package') + '.' + device.get('module')
        package = __import__(package_full_path, globals={}, locals={}, fromlist=[device.get('package')], level=-1)
        reload(modules[package_full_path])
        dObj = package.Device(device.get('id'), device)
        d = {}
        d['id'] = device.get('id')
        d['ffObject'] = pickle.dumps(dObj)
        d['config'] = device
        d['status'] = {}
        deviceDB.insert(d)


def install_child_device(deviceID, ffObject, config={}, status={}):
  logging.debug("Installing Child Device")
  d = {}
  d['id'] = deviceID
  d['ffObject'] = pickle.dumps(ffObject)
  d['config'] = config
  d['status'] = status
  deviceDB.insert(d)
      

def send_event(event):
  logging.info('send_event: ' + str(event))

  if event.sendToDevice:
    for d in deviceDB.find({'id':event.deviceID}):
      s = pickle.loads(d.get('ffObject'))
      s.sendEvent(event)
      d = pickle.dumps(s)
      deviceDB.update_one({'id':event.deviceID},{'$set': {'ffObject':d}, '$currentDate': {'lastModified': True}})

  for a in appsDB.find({'listen':event.deviceID}):
    app = pickle.loads(a.get('ffObject'))
    app.sendEvent(event)
    appObj = pickle.dumps(app)
    appsDB.update_one({'id':app.id},{'$set': {'ffObject':appObj}, '$currentDate': {'lastModified': True}})

  for d in  routineDB.find({'listen':event.deviceID}):
    s = pickle.loads(d.get('ffObject'))
    s.event(event)
  
  data_log(event.log, logType='event')

def send_command(command):
  global ffZwave
  logging.debug('send_command ' + str(command))

  sucess = False
  message = None

  if command.routine:
    routine = routineDB.find_one({'id':command.deviceID})
    if routine:
      s = pickle.loads(routine.get('ffObject'))
      s.executeRoutine(force=command.force)
      sucess = True

  if command.deviceID == ffZwave.name:
    ffZwave.sendCommand(command)

  for d in deviceDB.find({'id':command.deviceID}):
    s = pickle.loads(d.get('ffObject'))
    s.sendCommand(command)
    d = pickle.dumps(s)
    deviceDB.update_one({'id':command.deviceID},{'$set': {'ffObject':d}, '$currentDate': {'lastModified': True}})
    sucess = True

  for a in appsDB.find({'id':command.deviceID}):
    app = pickle.loads(a.get('ffObject'))
    app.sendCommand(command)
    appObj = pickle.dumps(app)
    appsDB.update_one({'id':app.id},{'$set': {'ffObject':appObj}, '$currentDate': {'lastModified': True}})
    sucess = True

  if not sucess:
    message = 'Device not found'
  data_log(command.log, message=message, logType='command')
  return sucess

  # MAYBE ALSO SEND TO APPS 

def send_request(request):
  logging.debug('send_request' + str(request))
  d = deviceDB.find_one({'id':request.deviceID})
  if d:
    if not request.forceRefresh:
      if request.all or request.multi:
        return d.get('status')
      else:
        return d.get('status').get(request.request)
    else:
      device = pickle.loads(d.get('ffObject'))
      data = device.requestData(request)
      return data
  return None

############################## HTTP UTILES ###########################################

def http_request(url,method='GET',headers=None,params=None,data=None,callback=None,json=True, code_only=False):
  request = treq.request(url=url,method=method,headers=headers,data=data)
  if callback:
    if code_only:
      request.addCallback(callback)
    if json:
      request.addCallback(json_callback, callback)
    else:
      request.addCallback(text_callback, callback)

def json_callback(response, callback):
  try:
    deferred = response.json()
    deferred.addCallback(callback)
  except:
    pass

def text_callback(response, callback):
  deferred = response.text()
  deferred.addCallback(callback)

############################## END HTTP UTILES ###########################################

def send_notification(deviceID, message, priority=0):
  if deviceID == 'all':
    for device in deviceDB.find({"config.subType":"notification"}):
      dID = device.get('id')
      notificationEvent = ffEvent(str(dID), {'notify': {'message' :message}})
  else:
    notificationEvent = ffEvent(deviceID, {'notify': {'message' :message}})

def read_settings():
  global core_settings
  with open('config/settings.json') as settings:
    logging.debug('Reading Settings')
    newSettings = json.load(settings)
    core_settings.port = newSettings.get('port')
    core_settings.ip_address = str(newSettings.get('ip_address'))
    logging.debug(core_settings)

## THIS WILL REPLACE THE TEST ONE ABOVE
def insatll_devices():
  device = {'package':'ffPresence', 'type':'device', 'deviceID':'Zach Presence', 'args':{}}
  print device
  package_full_path = device.get('type') + 's.' + device.get('package') + '.' + device.get('package')
  package = __import__(package_full_path, globals={}, locals={}, fromlist=[device.get('package')], level=-1)
  reload(package)
  package.Device(device.get('deviceID'), device)


def data_log(event, message=None, logType='unknown'):
  timestamp = datetime.now()
  datalogDB.insert({"timestamp":timestamp, "type":str(logType), "data":str(event), "message":str(message)})

def event_message(fromDevice, message):
  timestamp = datetime.now()
  messageDB.insert({"timestamp":timestamp, "message":str(message), "From":str(fromDevice)})


def update_status(status):
  deviceID = status.get('deviceID')
  device = deviceDB.find_one({'id':deviceID})
  if device:
    currentStatus = device.get('status')
    if currentStatus != status:
      deviceDB.update_one({'id':deviceID},{'$set': {'status': status}}) #, "$currentDate": {"lastModified": True}})
      return True
    else:
      return False
  else:
    return True

def auto_start():
  global ffZwave
  with open('config/devices.json') as devices:
    allDevices = json.load(devices)
    for name, device in allDevices.iteritems():
      if device.get('module') == "ffZwave":
        package_full_path = device.get('type') + 's.' + device.get('package') + '.' + device.get('module')
        package = __import__(package_full_path, globals={}, locals={}, fromlist=[device.get('package')], level=-1)
        ffZwave = package.Device(device.get('id'), device)
        #ffZwave.refresh_scheduler()

  for device in deviceDB.find({}):
    deviceID = device.get('id')
    ffEvent(deviceID, {'startup': True})


def run():
  global core_settings
  read_settings()
  auto_start()
  app.run(core_settings.ip_address, core_settings.port, logFile=open('logs/app.log','w'))

if __name__ == "__main__":
  run()