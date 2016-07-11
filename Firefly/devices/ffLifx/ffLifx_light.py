# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-03 09:18:26
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-27 17:21:40
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent
from webcolors import name_to_hex

PRESETS_CT = {
  'cloudy' : '6500K',
  'daylight' : '6000K',
  'noon' : '5200K',
  'sunny' : '5500K',
  'candle' : '2000K',
  'soft white' : '2700K',
  'warm white' : '3000K',
  'halogen' : '3200K',
  'fluorescent' : '4500K',
  'incandescent' : '2800K',

}

class Device(Device):
  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly LIFX Light',
      'type' : 'light',
      'package' : 'ffLifx',
      'module' : 'ffLifx_light'
    }
    self.COMMANDS = {
      'on' : self.setOn,
      'off' : self.setOff,
      'setLight' : self.setLight,
      'level' : self.setLevel,
      'switch' : self.switch,
      #'ctfade' : self.ctFade,
      'update' : self.update
    }
    self.REQUESTS = {
      'on': self.getOn,
      'hue' : self.getHue,
      'sat' : self.getSat,
      'ct' : self.getCt,
      'level' : self.getLevel,
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'lights',
      'dash_view' : {
        'request' : 'on',
        'type' : 'button', 
        'button' : {
          "false" : {
            'click' : 'true',
            'color' : 'grey',
            'command' : {'switch':'on'},
            'text' : 'Off'
          },
          "true" : {
            'click' : 'false',
            'color' : 'green lighten-1',
            'command' : {'switch':'off'},
            'default' : True,
            'text' : 'On'
          }
        }
      }
    }

    args = args.get('args')
    self._light_id = args.get('id')
    self._name = args.get('label')
    self._uuid = args.get('uuid')
    self._manufacturername = args.get('product').get('company')
    self._modelid = args.get('product').get('identifier')
    self._connected = args.get('connected')
    self._on = args.get('power')
    self._hue = args.get('color').get('hue')
    self._sat = args.get('color').get('saturation')
    self._bri = args.get('brightness')
    self._bridge = args.get('bridgeID')
    self._ct = args.get('color').get('kelvin')
    self._level = int(self._bri*100)

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################


  @property
  def on(self):
    return self._on

  @property
  def bri(self):
    return self._bri

  @property
  def ct(self):
    return self._ct

  @property
  def level(self):
    return self._level

  @property
  def hue(self):
      return self._hue

  def setOff(self, args={}):
    return self.setLight({'on':False})
  
  def setLevel(self, pLevel):
    return self.setLight({'level':pLevel})

  def setOn(self, args={}):
    return self.setLight({'on':True})

  def getOn(self):
    return self._on

  def getHue(self):
    return self._hue

  def getBri(self):
    return self._bri

  def getSat(self):
    return self._sat

  def getCt(self):
    return self._ct

  def getLevel(self):
    return self._level

  def setLight(self, value):
    lightValue = {}
    
    # HUE
    hue = value.get('hue')
    if hue:
      lightValue.update({'hue':hue})
      self._hue = hue

    #TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime:
      lightValue.update({'duration':transitiontime})

    #NAME COLOR
    name = value.get('name')
    if name:
      if name not in ['white','red','orange','yellow','cyan','green','blue','purple','pink']:
        value['hex'] = name_to_hex(name)
      else:
        lightValue.update({'name':name})

    #HEX COLOR
    hexColor = value.get('hex')
    if hexColor:
      lightValue.update({'hex':hexColor})

    # PRESET
    preset = value.get('preset')
    if preset:
      if preset in PRESETS_CT:
        value['ct'] = PRESETS_CT.get(preset)

    # SET FOR LEVEL
    level = value.get('level')
    if level:
      if level > 0:
        if level > 100:
          level = 100
        level = 100 if level >= 100 else level
        bri = int(level/100)
        level = level
        lightValue.update({'brightness':bri})
      if level <= 0:
        bri = 0
        level = 0
        self._on = False
        lightValue.update({'brightness':bri,'power':'off'})
      self._bri = bri
      self._level = level

    # SET CT:
    ct = value.get('ct')
    if ct:
      if 'K' in ct:
        ct = int(ct.replace('K',''))
      if ct < 2500:
        ct = 2500
      if ct > 9000:
        ct = 9000
      ct = str(ct) + 'K'
      lightValue.update({'kelvin':ct})
      self._ct = ct

    # SET FOR ON
    on = value.get('on')
    if on is not None:
      if on:
        lightValue.update({'power':'on'})
      else:
        lightValue.update({'power':'off'})
      self._on = on

    self.set_light(lightValue)
    return value

  def switch(self, value):
    if value == 'on':
      self.setLight({'on':True})
    elif value == 'off':
      self.setLight({'on':False})

  def set_light(self, value):
    logging.critical("SET_LIGHT")
    ffCommand(self._bridge, {'sendLightCommand':{'lightCommand':value,'lightID': self._light_id}})

  def update(self, args={}):
    self._connected = args.get('connected')
    self._on = args.get('power')
    self._hue = args.get('color').get('hue')
    self._sat = args.get('color').get('saturation')
    self._bri = args.get('brightness')
    self._bridge = args.get('bridgeID')
    self._ct = args.get('color').get('kelvin')
    self._level = int(self._bri*100)
