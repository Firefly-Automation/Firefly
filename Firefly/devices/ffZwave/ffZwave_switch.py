# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-25 00:40:41
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-08 19:20:29
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Zwave Switch',
      'type' : 'switch',
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
    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'lights',
      'dash_view' : {
        'request' : 'on',
        'type' : 'switch', 
        'switch' : {
          "false" : {
            'command' : {'switch':'off'},
            'text' : 'Off'
          },
          "true" : {
            'command' : {'switch':'on'},
            'default' : True,
            'text' : 'On'
          }
        }
      },
      'card' : "<md-card layout='row' layout-align='center center' layout-wrap><device-card layout='row' flex layout-wrap layout-align='center center'><span  style='cursor: pointer;' ng-click='selectDeviceIndex($index)' layout-align='start center' flex=''> {{::item.name}} </span><md-switch layout-align='end center' ng-model=deviceStates[item.id].state ng-click='switch(!deviceStates[item.id].state)'></md-switch></device-card></div><md-card-content ng-if='$index ==selectedDeviceIndex' flex=100 layout-wrap><md-divider></md-divider><div layout='row' layout-align='center center'><md-button flex=50 ng-click='switch(true)'>On</md-button><md-button flex=50 ng-click='switch(false)'>Off</md-button></div><md-divider></md-divider><md-subhead> Turn off in: </md-subhead> <div layout='row' layout-align='center center'><md-button flex=25>30m</md-button><md-button flex=25>1h</md-button><md-button flex=25>2h</md-button><md-button flex=25>4h</md-button></div><br><md-card-actions layout='row' layout-align='start center' flex='100'><md-button flex=50>More Info</md-button></md-card-actions></md-card-content></md-card>"
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