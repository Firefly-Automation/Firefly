# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 01:25:27
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-08 19:51:13

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
      'presence': self.getPresence
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'presence',
      'dash_view': {
        'request': 'presence',
        'type': 'text', 
        'text': {
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
      },
      'card': "<md-card layout='row' layout-align='center center' layout-wrap><device-card layout='row' flex layout-wrap layout-align='center center'><span  style='cursor: pointer;' ng-click='selectDeviceIndex($index)' layout-align='start center' flex=''> {{::item.name}} </span><div layout-align='end center' ng-show='deviceStates[item.id].presence'>Present</div><div layout-align='end center' ng-show='!deviceStates[item.id].presence'>Not Present</div></device-card></div><md-card-content ng-show='$index ==selectedDeviceIndex' flex=100 layout-wrap><md-divider></md-divider><div layout='row' layout-align='center center'><md-button flex=50 ng-click='presence(true)'>Present</md-button><md-button flex=50 ng-click='presence(false)'>Not Present</md-button></div><md-divider></md-divider><md-card-actions layout='row' layout-align='start center' flex='100'><md-button flex=50>More Info</md-button></md-card-actions></md-card-content></md-card>"
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
