# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-25 00:40:41
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-25 18:00:21
from core.models.device import Device
from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent
import logging

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Zwave Switch',
      'type' : 'sensor',
      'package' : 'ffZwave',
      'module' : 'ffZwave_switch'
    }
    
    self.COMMANDS = {
      'update' : self.update,
      'on' : self.setOn,
      'off' : self.setOff,
      'switch' : self.switch
    }

    self.REQUESTS = {
      'state' : self.getState,
      'on' : self.getOn,
      'off' : self.getOff,
      'valueId' : self.getValueId,
      'label' : self.getLabel
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')

    self._state = False

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

  def getState(self, args={}):
    return self._state

  def getOn(self, args={}):
    return self._state

  def getOff(self, args={}):
    return not self._state

  def setOn(self, args={}):
    self._state = True
    ffCommand(self._controller_id,{'switch' : {'node':self._node, 'on':True}})

  def setOff(self, args={}):
    self._state = False
    ffCommand(self._controller_id,{'switch' : {'node':self._node, 'on':False}})

  def switch(self, value):
    if value == 'on' or value is True:
      self.setOn()
    else:
      self.setOff()

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

    if args.get('Switch'):
      self._state = args.get('Switch').get('data')

    for item, value in args.iteritems():
      setattr(self, str(item), value)
      setattr(self, str(value.get('value_id')), value)