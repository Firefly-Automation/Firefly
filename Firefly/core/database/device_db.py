# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-12 23:18:17
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 23:21:11

from core import deviceDB

def getDeviceList(lower=True):
  device_list = {}
  for d in deviceDB.find({},{"config.name":1,"id":1}):
    if d.get('config').get('name') is not None:
      if lower:
        device_list[d.get('config').get('name').lower()] = d.get('id')
      else:
        device_list[d.get('config').get('name')] = d.get('id')
  return device_list

def getDeviceViewsList():
  devices = []
  for d in deviceDB.find({},{'status.views':1, 'id':1}):
    dID = d.get('id')
    if (d.get('status').get('views')):
      devices.append(d.get('status').get('views'))
  return devices