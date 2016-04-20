# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-19 21:57:10
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-19 22:32:54


class Notification(object):
  def __init__(self, deviceID, message, priority=0):
    self._deviceID = deviceID
    self._message = message
    self._priority = priority

    if self._deviceID.lower() == 'all':
      self.send_all()
    else:
      self.send()

  def send_all(self):
    from pymongo import MongoClient
    from core.models.command import Command as ffCommand
    client = MongoClient()
    ffDB = client.ff
    deviceDB = ffDB.devices
    for device in deviceDB.find({"config.subType":"notification"}):
      dID = device.get('id')
      notificationEvent = ffCommand(str(dID), {'notify': {'message' :self._message}})

  def send(self):
    from core.models.command import Command as ffCommand
    notificationEvent = ffCommand(self._deviceID, {'notify': {'message' :self._message}})