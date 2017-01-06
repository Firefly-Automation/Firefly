# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-12 23:18:17
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-12-24 20:09:31

import json
import re
import pickle
import os

from core import deviceDB
from sys import modules

from core import ffScheduler
from core import configPath

class DeviceViews(object):

  def __init__(self):
    self.deviceViewsList = getDeviceViewsList()
    self.deviceStatusDict = getDeviceStatusDict()

    ffScheduler.runEveryS(4, self.refreshViews, job_id='Device_Refresher')

  def refreshViews(self):
    self.deviceViewsList = getDeviceViewsList()
    self.deviceStatusDict = getDeviceStatusDict()


def getDeviceList(lower=True):
  device_list = {}
  for d in deviceDB.find({},{"config.name":1,"id":1}):
    if d.get('config').get('name') is not None:
      if lower:
        device_list[d.get('config').get('name').lower()] = d.get('id')
      else:
        device_list[d.get('config').get('name')] = d.get('id')
  return device_list

def getDeviceViewsList(filters=['hgrp-']):
  devices = []
  for d in deviceDB.find({},{'status.views':1, 'id':1}):
    if (d.get('status').get('views')):
      for f in filters:
        if d.get('status').get('views').get('name').find(f) != -1:
          continue
        devices.append(d.get('status').get('views'))
  return devices

def getDeviceInfo(filters=None):
  devices = {}
  for d in deviceDB.find({}):
    if not d.get('config').get('name'):
      continue
    if d.get('config').get('name') is not None:
      if filters:
        if d.get('type') not in filters:
          continue
      devices[d.get('config').get('name')] = {
        'name': d.get('config').get('name'),
        'type': d.get('type'),
        'subtype': d.get('config').get('subtype'),
        'commands': d.get('commands'),
        'id': d.get('id')
      }
  return devices

def getDeviceStatusDict():
  devices = {}
  for d in deviceDB.find({},{'status':1, 'id':1}):
    d_id = d.get('id')
    if (d.get('status')):
      devices[d_id] = d.get('status')
  return devices

def reinstall_indigo():
  from core import ffIndigo
  if ffIndigo:
    deviceDB.remove({'id': re.compile('indigo-.*')})
    ffIndigo.install_devices()


def reinstallDevices():
  deviceDB.remove({})
  from core import ffNest
  reinstall_indigo()
  with open(os.path.join(configPath,'devices.json')) as devices:
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
        try:
          d['commands'] = dObj.commands
        except:
          d['commands'] = []
        try: 
          d['type'] = dObj.type
        except:
          d['type'] = 'UNKNOWN'
        deviceDB.insert(d)
