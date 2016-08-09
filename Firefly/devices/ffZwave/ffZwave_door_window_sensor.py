# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-25 00:40:41
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-07-05 08:54:48
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Zwave Door/Window Sensor',
      'type' : 'sensor',
      'package' : 'ffZwave',
      'module' : 'ffZwave_door_window_sensor'
    }
    
    self.COMMANDS = {
      'update' : self.update
    }

    self.REQUESTS = {
      'state' : self.getState,
      'open' : self.getOpen,
      'closed' : self.getClosed,
      'alarm' : self.getAlarm,
      'battery' : self.getBattery,
      'valueId' : self.getValueId,
      'label' : self.getLabel
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('name'),
      'id' : deviceID,
      'type' : 'sensor',
      'dash_view' : {
        'request' : 'state',
        'type' : 'text', 
        'text' : {
          "false" : {
            'color' : 'blue',
            'command' : 'none',
            'text' : 'Closed'
          },
          "true" : {
            'click' : 'true',
            'color' : 'red',
            'command' : 'none',
            'text' : 'Open'
          }
        }
      }
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')

    self._state = False
    self._battery = None
    self._alarm = False

    self._controller_id = args.get('controller_id')
    #These should all be none on first install
    self._node = args.get('node')
    self._manufacturer_name = args.get('manufacturer_name')
    self._product_name = args.get('product_name')
    self._product_id = args.get('product_id')
    self._product_type = args.get('product_type')
    self._device_type = args.get('device_type')
    self._command_classes_as_string = args.get('command_classes_as_string')
    self._ready = args.get('ready')
    self._failed = args.get('failed')



    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

####################### START OF DEVICE CODE #############################

  def getClosed(self, args={}):
    return not self._state

  def getOpen(self, args={}):
    return self._state

  def getBattery(self, args={}):
    return self._battery

  def getState(self, args={}):
    return self._state

  def getAlarm(self, args={}):
    return self._alarm

  def getValueId(self, args={}):
    valueId = args.get('value_id')
    return getattr(self,str(valueId), -1)

  def getLabel(self, args={}):
    label = args.get('label')
    return getattr(self, str(label), -1)


  def update(self, args={}):
    self._node = args.get('node')
    self._manufacturer_name = args.get('manufacturer_name')
    self._product_name = args.get('product_name')
    self._product_id = args.get('product_id')
    self._product_type = args.get('product_type')
    self._device_type = args.get('device_type')
    self._command_classes_as_string = args.get('command_classes_as_string')
    self._ready = args.get('ready')
    self._failed = args.get('failed')

    args = args.get('data')

    if args.get('Alarm Level'):
      self._alarm = True if args.get('Alarm Level').get('data') >= 127 else False

    if args.get('Sensor'):
      self._state = args.get('Sensor').get('data')

    if args.get('Battery Level'):
      self._battery = args.get('Battery Level').get('data')

    for item, value in args.iteritems():
      setattr(self, str(item), value)
      setattr(self, str(value.get('value_id')), value)