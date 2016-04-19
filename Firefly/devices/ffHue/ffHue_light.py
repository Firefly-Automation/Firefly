# -*- coding: utf-8 -*-
# @Author: zpriddy
# @Date:   2016-04-17 20:28:40
# @Last Modified by:   zpriddy
# @Last Modified time: 2016-04-18 21:20:21

from core.models.device import Device
from core.models.command import Command as ffCommand
from core.models.event import Event as ffEvent
import logging
from rgb_cie import Converter
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

converter = Converter()

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Hue Light Device',
      'type' : 'light',
      'package' : 'ffHue',
      'module' : 'ffHue_light'
    }
    
    self.COMMANDS = {
      'on' : self.setOn,
      'off' : self.off,
      'setLight' : self.setLight,
      'level' : self.setLevel,
      'bri' : self.setBri,
      'switch' : self.switch,
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
    self._light_id = args.get('lightID')
    self._name = args.get('name')
    self._uniqueid = args.get('uniqueid')
    self._manufacturername = args.get('manufacturername')
    self._swversion = args.get('swversion')
    self._modelid = args.get('modelid')
    self._reachable = args.get('state').get('reachable')
    self._on = args.get('state').get('on')
    self._hue = args.get('state').get('hue')
    self._sat = args.get('state').get('sat')
    self._effect = args.get('state').get('effect')
    self._xy = args.get('state').get('xy')
    self._colormode = args.get('state').get('colormode')
    self._alert = args.get('state').get('alert')
    self._bri = args.get('state').get('bri')
    self._reachable = args.get('state').get('reachable')
    self._type = args.get('type')
    self._bridge = args.get('bridgeID')
    self._ct = args.get('state').get('ct')
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
    self.set_light({'on':value})
    

  def off(self, args={}):
    self.set_light({'on':False})
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
      self._on = True
      self._level = pLevel
      self._bri = int(255/100*pLevel)
    self.set_light({'bri':self._bri,'on':self.on})

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
      self._bri = pBri
      self._on = True
    self.set_light({'bri':self._bri,'on':self.on})

  # setLight(self, value={'hex','level','bri','x','y','hue','on','ct'}) -> Parse from these arguments :) ONE BIG PARSER
  def setLight(self, value):
    lightValue = {}

    # XY
    xy = value.get('xy')
    if xy:
      lightValue.update({'xy':xy})
      print lightValue

    # HUE
    hue = value.get('hue')
    if hue:
      lightValue.update({'hue':hue})

    #TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime:
      lightValue.update({'transitiontime':transitiontime})
    else:
      lightValue.update({'transitiontime':40})


    #NAME COLOR
    name = value.get('name')
    if name:
      value['hex'] = name_to_hex(name)


    #HEX COLOR
    hexColor = value.get('hex')
    if hexColor:
      lightValue.update(self.hexColor(hexColor))
      self._on = True if not value.get('noOn') else self.on
      lightValue.update({'on':self.on})

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
        self._bri = int(255/100*level)
        self._level = level
        self._on = True if not value.get('noOn') else self.on
        lightValue.update({'bri':self.bri,'on':self.on})
      if level <= 0:
        self._bri = 0
        self._level = 0
        self._on = False
        lightValue.update({'bri':self.bri,'on':self.on})

    # SET FOR BRI
    bri = value.get('bri')
    if bri:
      if bri > 0:
        self._level = int(self._bri/255*100)
        self._bri = bri
        sself._on = True if not value.get('noOn') else self.on 
        lightValue.update({'bri':self.bri,'on':self.on})
      if bri <= 0:
        self._level = 0
        self._bri = 0
        self._on = False
        lightValue.update({'bri':self.bri,'on':self.on})

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
      lightValue.update({'ct':self.ct, 'on':self.on})


    # SET FOR ON
    on = value.get('on')
    if on is not None:
      self._on = on
      lightValue.update({'on':self.on})

    # EFFECT
    effect = value.get('effect')
    if effect:
      self._effect = effect
      lightValue.update({'effect':self._effect})

    # ALERT
    alert = value.get('alert')
    if alert:
      self._alert = alert
      lightValue.update({'alert':alert})

    self.set_light(lightValue)



  

  @property
  def hue(self):
      return self._hue

  def switch(self, value):
    if value == 'on':
      self.on = True
    elif value == 'off':
      self.on = False

  def set_light(self, value):
    light_id = self._light_id
    lightEvent = ffCommand(self._bridge,{'sendLightRequest' : {'lightID':light_id,'data':value}})

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
    self._reachable = raw_data.get('state').get('reachable')
    self._on = raw_data.get('state').get('on')
    self._hue = raw_data.get('state').get('hue')
    self._sat = raw_data.get('state').get('sat')
    self._effect = raw_data.get('state').get('effect')
    self._xy = raw_data.get('state').get('xy')
    self._colormode = raw_data.get('state').get('colormode')
    self._alert = raw_data.get('state').get('alert')
    self._bri = raw_data.get('state').get('bri')
    self._reachable = raw_data.get('state').get('reachable')
    self._ct = raw_data.get('state').get('ct')
    self._level = int(self._bri/255*100)
    raw_data['state']['level'] = self._level
    ffEvent(self._id,raw_data.get('state'))