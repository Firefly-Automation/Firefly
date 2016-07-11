# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 20:28:40
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-27 17:22:02

import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent
from ctFade import CTFade
from math import ceil
from rgb_cie import Converter
from webcolors import name_to_hex

ctFade = CTFade(0,0,0,0,None, None,run=False)

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

converter = Converter()

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Hue Group Device',
      'type' : 'group',
      'package' : 'ffHue',
      'module' : 'ffHue_group'
    }
    
    self.COMMANDS = {
      'on' : self.setOn,
      'off' : self.setOff,
      'setLight' : self.setGroup,
      'level' : self.setLevel,
      'bri' : self.setBri,
      'switch' : self.switch,
      'ctfade' : self.ctFade,
      'update' : self.update
    }

    self.REQUESTS = {
      'on': self.getOn,
      'hue' : self.getHue,
      'bri' : self.getBri,
      'sat' : self.getSat,
      'ct' : self.getCt,
      'xy' : self.getXy,
      'type' : self.getType,
      'level' : self.getLevel
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

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._group_id = args.get('groupID')
    self._name = args.get('name')
    self._lights = args.get('lights')
    self._on = args.get('action').get('on')
    self._hue = args.get('action').get('hue')
    self._sat = args.get('action').get('sat')
    self._effect = args.get('action').get('effect')
    self._xy = args.get('action').get('xy')
    self._colormode = args.get('action').get('colormode')
    self._alert = args.get('action').get('alert')
    self._bri = args.get('action').get('bri')
    self._ct = args.get('action').get('ct')
    self._type = args.get('type')
    self._bridge = args.get('bridgeID')
    self._level = int(self._bri/255.0*100.0)

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

####################### START OF DEVICE CODE #############################

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
  def tyep(self):
    return self._type

  @property
  def hue(self):
      return self._hue

  def setOff(self, args={}):
    return self.setGroup({'on':False})
  
  def setLevel(self, pLevel):
    return self.setGroup({'level':pLevel})

  def setBri(self, pBri):
    return self.setGroup({'bri':pBri})

  def setOn(self, args={}):
    return self.setGroup({'on':True})

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

  def getXy(self):
    return self._xy

  def getType(self):
    return self._type

  def getLevel(self):
    self._level = int(ceil(self._bri/255.0*100.0))
    return self._level

  def setGroup(self, value):
    groupValue = {}

    # END FADE IF SET COMMAND IS GIVEN
    if value.get('ctfade') is None:
      global ctFade
      ctFade.endRun()

    # XY
    xy = value.get('xy')
    if xy:
      groupValue.update({'xy':xy})
      self._xy = xy

    # HUE
    hue = value.get('hue')
    if hue:
      groupValue.update({'hue':hue})
      self._hue = hue

    #TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime:
      groupValue.update({'transitiontime':transitiontime})



    #NAME COLOR
    name = value.get('name')
    if name:
      value['hex'] = name_to_hex(name)


    #HEX COLOR
    hexColor = value.get('hex')
    if hexColor:
      groupValue.update(self.hexColor(hexColor))


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
        bri = int(255.0/100.0*level)
        level = level
        groupValue.update({'bri':bri})
      if level <= 0:
        bri = 0
        level = 0
        self._on = False
        groupValue.update({'bri':bri,'on':False})
      self._bri = bri
      self._level = level

    # SET FOR BRI
    bri = value.get('bri')
    if bri:
      if bri > 255:
        bri = 255
        self._level = int(bri/255.0*100.0)
      if bri <= 0:
        bri = 0
        self._level = 0
        self._on = False
        groupValue.update({'on':False})
      groupValue.update({'bri':bri})
      self._bri = bri

    # SET CT:
    ct = value.get('ct')
    if ct:
      if 'K' in ct.upper():
        ct = int(ct.upper().replace('K',''))
        ct = int(1000000/ct)
      if ct > 500:
        ct = 500
      if ct < 153:
        ct = 153
      
      groupValue.update({'ct':ct})
      self._ct = ct

    # EFFECT
    effect = value.get('effect')
    if effect:
      groupValue.update({'effect':effect})
      self._effect = effect

    # ALERT
    alert = value.get('alert')
    if alert:
      groupValue.update({'alert':alert})
      self._alert = alert

    # SET FOR ON
    on = value.get('on')
    if on is not None:
      groupValue.update({'on':on})
      self._on = on

    # Turn lights on unless told not to or has already been set
    if groupValue.get('on') is None and not value.get('onOn'):
      groupValue.update({'on':True})
      self._on = True

    self.set_group(groupValue)
    return value


  def ctFade(self, args={}):
    global ctFade
    ctFade = CTFade(str(self._id),args.get('startK'),args.get('endK'),args.get('fadeS'), args.get('startL'), args.get('endL'))

  def switch(self, value):
    if value == 'on':
      self.setGroup({'on':True})
    elif value == 'off':
      self.setGroup({'on':False})

  def set_group(self, value):
    group_id = self._group_id
    groupCommand = ffCommand(self._bridge,{'sendGroupRequest' : {'groupID':group_id,'data':value}})


  def hexColor(self, colorHex):
    if '#' in colorHex:
      colorHex = colorHex.replace('#','')
    return {'xy':converter.hexToCIE1931(colorHex)}


  def update(self, raw_data):
    self._lights = raw_data.get('lights')
    self._on = raw_data.get('action').get('on')
    self._hue = raw_data.get('action').get('hue')
    self._sat = raw_data.get('action').get('sat')
    self._effect = raw_data.get('action').get('effect')
    self._xy = raw_data.get('action').get('xy')
    self._colormode = raw_data.get('action').get('colormode')
    self._alert = raw_data.get('action').get('alert')
    self._bri = raw_data.get('action').get('bri')
    self._ct = raw_data.get('action').get('ct')
    self._type = raw_data.get('type')
    self._level = int(ceil(self._bri/255.0*100.0))

    #ffEvent(self._id, raw_data.get('action'))
