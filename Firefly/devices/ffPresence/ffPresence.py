# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 01:25:27
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-07-05 00:19:34

import logging

from core.models.device import Device

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Presence Device',
      'type' : 'presence',
      'package' : 'ffPresence',
      'module' : 'ffPresence'
    }
    
    self.COMMANDS = {
      'presence' : self.setPresence,
      'startup' : self.refreshData
    }

    self.REQUESTS = {
      'presence' : self.getPresence
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'presence',
      'dash_view' : {
        'request' : 'presence',
        'type' : 'text', 
        'text' : {
          "false" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : {'presence':True},
            'text' : 'Away'
          },
          "true" : {
            'click' : 'false',
            'color' : 'green',
            'command' : {'presence':False},
            'default' : True,
            'text' : 'Present'
          }
        }
      }
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._notify_present = args.get('notify_present')
    self._notify_not_present = args.get('notify_not_present')
    self._notify_device = args.get('notify_device')
    self._presence = True

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################


  def setPresence(self, value):
    from core.firefly_api import event_message
    if value is not self.presence:
      self._presence = value
      event_message(self._name, "Setting Presence To " + str(value))
      logging.debug("Setting Presence To " + str(value))

      

  def getPresence(self):
    return self._presence

  @property
  def presence(self):
    return self._presence

  @presence.setter
  def presence(self, value):
    self._presence = value