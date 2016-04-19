# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 20:28:40
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-18 21:42:08

from core.models.device import Device
from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent
import logging
from rgb_cie import Converter
from webcolors import name_to_hex
from ctFade import CTFade

ctFade = CTFade(0,0,0,0,run=False)

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
      'off' : self.off,
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
      'type' : self.getType
    }
    print args
    args = args.get('args')
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
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
    self._level = int(self._bri/255*100)


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

  @on.setter
  def on(self, value):
    self._on = value
    self.set_group({'on':value})
    

  def off(self, args={}):
    self.set_group({'on':False})
    self._on = False
    return {'switch' : 'off'}

  @property
  def level(self):
    return self._level

  @property
  def tyep(self):
    return self._tyep
  

  @level.setter
  def level(self, pLevel=100):
    if pLevel == 0:
      self._level = 0
      self._bri = 0
      self._on = False
    else:
      on = True
      self._level = pLevel
      bri = int(255/100*pLevel)
    self.set_group({'bri':bri,'on':on})

  def setLevel(self, pLevel):
    if pLevel <= 0:
      pLevel = 0
    if pLevel > 100:
      pLevel = 100
    self.level = pLevel

  def setBri(self, pBri):
    if pBri <= 0:
      self._bri = 0
      self._on = False
    else:
      if pBri > 255:
        pBri = 255
      bri = pBri
      on = True
    self.set_group({'bri':bri,'on':on})

  # setGroup(self, value={'hex','level','bri','x','y','hue','on','ct'}) -> Parse from these arguments :) ONE BIG PARSER
  ## TODO FIX ALL THE self._* to just * = then set the self._* but dont use them 
  def setGroup(self, value):
    groupValue = {}

    # XY
    xy = value.get('xy')
    if xy:
      groupValue.update({'xy':xy})
      print groupValue

    # HUE
    hue = value.get('hue')
    if hue:
      groupValue.update({'hue':hue})

    #TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime:
      groupValue.update({'transitiontime':transitiontime})
    else:
      groupValue.update({'transitiontime':40})


    #NAME COLOR
    name = value.get('name')
    if name:
      value['hex'] = name_to_hex(name)


    #HEX COLOR
    hexColor = value.get('hex')
    if hexColor:
      groupValue.update(self.hexColor(hexColor))
      self._on = True if not value.get('noOn') else self.on
      groupValue.update({'on':self.on})

    # PRESET
    preset = value.get('preset')
    if preset:
      if preset in PRESETS_CT:
        value['ct'] = PRESETS_CT.get(preset)


    # SET FOR LEVEL
    level = value.get('level')
    if level:
      if level > 0:
        level = 100 if level >= 100 else level
        bri = int(255.0/100.0*level)
        level = level
        on = True if not value.get('noOn') else self.on
        groupValue.update({'bri':bri,'on':on})
      if level <= 0:
        self._bri = 0
        self._level = 0
        self._on = False
        groupValue.update({'bri':self.bri,'on':self.on})

    # SET FOR BRI
    bri = value.get('bri')
    if bri:
      if bri > 0:
        self._level = int(self._bri/255.0*100.0)
        self._bri = bri
        sself._on = True if not value.get('noOn') else self.on 
        groupValue.update({'bri':self.bri,'on':self.on})
      if bri <= 0:
        self._level = 0
        self._bri = 0
        self._on = False
        groupValue.update({'bri':self.bri,'on':self.on})

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
      self._ct = ct
      self._on = True if not value.get('noOn') else self.on
      groupValue.update({'ct':self.ct, 'on':self.on})


    # SET FOR ON
    on = value.get('on')
    if on is not None:
      self._on = on
      groupValue.update({'on':self.on})

    # EFFECT
    effect = value.get('effect')
    if effect:
      self._effect = effect
      groupValue.update({'effect':self._effect})

    # ALERT
    alert = value.get('alert')
    if alert:
      self._alert = alert
      groupValue.update({'alert':alert})

    self.set_group(groupValue)


  def ctFade(self, args={}):
    global ctFade
    #{"device":"hue-group-4", "command":"ctfade":{"startK":6500,"endK":2700,"fadeS":900}}}
    print '================================================================================'
    print args
    ctFade = CTFade(str(self._id),args.get('startK'),args.get('endK'),args.get('fadeS'))
  

  @property
  def hue(self):
      return self._hue

  def switch(self, value):
    if value == 'on':
      self.on = True
    elif value == 'off':
      self.on = False

  def set_group(self, value):
    group_id = self._group_id
    groupEvent = ffCommand(self._bridge,{'sendGroupRequest' : {'groupID':group_id,'data':value}})

  def setOn(self, args={}):
    self.on = True
    return {'switch' : 'on'}

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

  def hexColor(self, colorHex):
    if '#' in colorHex:
      colorHex = colorHex.replace('#','')

    if 'LST' in self._modelid:
      return {'xy':converter.hexToCIE1931(colorHex, lightType='LST')}

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
    self._level = int(self._bri/255*100)
    raw_data['action']['level'] = self._level

    ffEvent(self._id, raw_data.get('action'))
