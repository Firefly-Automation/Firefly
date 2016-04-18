# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 01:25:27
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-17 20:34:09

from core.models.device import Device
import logging

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Presence Device',
      'type' : 'presence',
      'package' : 'ffPresence',
      'module' : 'ffPresence'
    }
    
    self.COMMANDS = {
      'presence' : self.setPresence
    }

    self.REQUESTS = {
      'presence' : self.getPresence
    }
    args = args.get('args')
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)

    self._notify_present = args.get('notify_present')
    self.notify_not_present = args.get('notify_not_present')
    self.notify_device = args.get('notify_device')
    self._presence = True

  def setPresence(self, value):
    from core.firefly_api import event_message
    if value is not self.presence:
      self.presence = value
      event_message(self._name, "Setting Presence To " + str(value))
      logging.debug("Setting Presence To " + str(value))
      

  def getPresence(self):
    return self.presence

  @property
  def presence(self):
      return self._presence

  @presence.setter
  def presence(self, value):
    self._presence = value