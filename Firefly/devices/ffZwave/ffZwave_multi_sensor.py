# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-25 00:40:41
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-08 19:11:00
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Zwave Multi Sensor',
      'type' : 'sensor',
      'package' : 'ffZwave',
      'module' : 'ffZwave_multi_sensor'
    }
    
    self.COMMANDS = {
      'update' : self.update
    }

    self.REQUESTS = {
      'motion' : self.getMotion,
      'temperature' : self.getTemperature,
      'temperatureUnits' : self.getTemperatureUnits,
      'humidity' : self.getHumidity,
      'humidityUnits' : self.getHumidityUnits,
      'luminance' : self.getLuminance,
      'luminanceUnits' : self.getLuminanceUnits,
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
        'request' : 'motion',
        'type' : 'text', 
        'text' : {
          "false" : {
            'color' : 'grey',
            'command' : 'none',
            'text' : 'Inactive'
          },
          "true" : {
            'color' : 'blue',
            'command' : 'none',
            'text' : 'Active'
          }
        }
      },
      'card': "<md-card layout='row' layout-align='center center' layout-wrap><device-card layout='row' flex layout-wrap layout-align='center center'><span  style='cursor: pointer;' ng-click='selectDeviceIndex($index)' layout-align='start center' flex=''> {{::item.name}} </span><div layout-align='end center' ng-show='deviceStates[item.id].motion'>Active</div><div layout-align='end center' ng-show='!deviceStates[item.id].motion'>Inactive</div></device-card></div><md-card-content ng-show='$index ==selectedDeviceIndex' flex=100 layout-wrap><md-card-actions layout='row' layout-align='start center' flex='100'><md-button flex=50>More Info</md-button></md-card-actions></md-card-content></md-card>"
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')

    self._motion = False
    self._temperature = -1
    self._temperature_units = None
    self._humidity = -1
    self._humidity_units = None
    self._luminance = -1
    self._luminance_units = None
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

  def getMotion(self, args={}):
    return self._motion

  def getHumidity(self, args={}):
    return self._humidity

  def getHumidityUnits(self, args={}):
    return self._humidity_units

  def getLuminance(self, args={}):
    return self._luminance

  def getLuminanceUnits(self, args={}):
    return self._luminance_units

  def getTemperature(self, args={}):
    return self._temperature

  def getTemperatureUnits(self, args={}):
    return self._temperature_units

  def getAlarm(self, args={}):
    return self._alarm

  def getBattery(self, args={}):
    return self._battery

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
      self._motion = args.get('Sensor').get('data')

    if args.get('Luminance'):
      self._luminance = args.get('Luminance').get('data')
      self._luminance_units = args.get('Luminance').get('units')

    if args.get('Relative Humidity'):
      self._humidity = args.get('Relative Humidity').get('data')
      self._humidity_units = args.get('Relative Humidity').get('units')

    if args.get('Temperature'):
      self._temperature = args.get('Temperature').get('data')
      self._temperature_units = args.get('Temperature').get('units')

    if args.get('Battery Level'):
      self._battery = args.get('Battery Level').get('data')

    for item, value in args.iteritems():
      setattr(self, str(item), value)
      setattr(self, str(value.get('value_id')), value)