from Firefly import logging
from Firefly.const import (EVENT_ACTION_OFF, EVENT_ACTION_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF,
                           EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH, DEVICE_TYPE_COLOR_LIGHT, COMMAND_UPDATE, ACTION_LEVEL,
                           LEVEL)
from Firefly.components.virtual_devices import AUTHOR
from Firefly.helpers.device import Device
# from rgb_cie import Converter
from Firefly.helpers.events import Command

from Firefly.helpers.metadata import metaSwitch, metaDimmer

TITLE = 'Firefly Hue Device'
DEVICE_TYPE = DEVICE_TYPE_COLOR_LIGHT
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
INITIAL_VALUES = {'_state':            EVENT_ACTION_OFF,
                  '_uniqueid':         '-1',
                  '_manufacturername': 'unknown',
                  '_on':               EVENT_ACTION_OFF,
                  '_hue':              0,
                  '_sat':              0,
                  '_effect':           False,
                  '_xy':               0,
                  '_colormode':        'unknown',
                  '_alert':            False,
                  '_bri':              0,
                  '_reachable':        False,
                  '_type':             'unknown',
                  '_ct':               0,
                  '_level':            0,
                  '_hue_noun':         'state',
                  '_hue_service':      'service_hue',
                  '_hue_number':       -1
                  }


class HueDevice(Device):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):
    if not kwargs.get('initial_values'):
      kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, title, author, commands, requests, device_type, **kwargs)

    self.__dict__.update(kwargs['initial_values'])

    if self._alias == self.id:
      self._alias = kwargs.get('name')


    # TODO: Remove hue_bridge?
    self._hue_bridge = kwargs.get('hue_bridge')
    self._hue_service = kwargs.get('hue_service')

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command(COMMAND_UPDATE, self.update)
    self.add_command(ACTION_LEVEL, self.set_level)

    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

    self.add_request(STATE, self.get_state)

    self.add_action(STATE, metaSwitch())
    self.add_action(LEVEL, metaDimmer())

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_COLOR_LIGHT', STATE)

    self._hue_noun = 'state' if self._package == 'Firefly.components.hue.hue_light' else 'action'

    if self._hue_noun == 'state':
      self._hue_type = 'light'
    else:
      self._hue_type = 'group'
    self._hue_number = kwargs.get('hue_number')

    self._name = kwargs.get('name')
    self._uniqueid = kwargs.get('uniqueid')
    self._manufacturername = kwargs.get('manufacturername')
    self._swversion = kwargs.get('swversion')
    self._modelid = kwargs.get('modelid')
    self._bri = 0

    if kwargs.get(self.hue_noun):
      self._on = kwargs.get(self.hue_noun).get('on')
      self._hue = kwargs.get(self.hue_noun).get('hue')
      self._sat = kwargs.get(self.hue_noun).get('sat')
      self._effect = kwargs.get(self.hue_noun).get('effect')
      self._xy = kwargs.get(self.hue_noun).get('xy')
      self._colormode = kwargs.get(self.hue_noun).get('colormode')
      self._alert = kwargs.get(self.hue_noun).get('alert')
      self._bri = kwargs.get(self.hue_noun).get('bri')
      self._reachable = kwargs.get(self.hue_noun).get('reachable')
      self._ct = kwargs.get(self.hue_noun).get('ct')

    self._level = int(self._bri / 255.0 * 100.0)

  def update(self, **kwargs):
    self._name = kwargs.get('name')
    self._uniqueid = kwargs.get('uniqueid')
    self._manufacturername = kwargs.get('manufacturername')
    self._swversion = kwargs.get('swversion')
    self._modelid = kwargs.get('modelid')
    self._hue_service = kwargs.get('hue_service')
    self._hue_number = kwargs.get('hue_number')

    if kwargs.get(self.hue_noun):
      self._on = kwargs.get(self.hue_noun).get('on')
      self._hue = kwargs.get(self.hue_noun).get('hue')
      self._sat = kwargs.get(self.hue_noun).get('sat')
      self._effect = kwargs.get(self.hue_noun).get('effect')
      self._xy = kwargs.get(self.hue_noun).get('xy')
      self._colormode = kwargs.get(self.hue_noun).get('colormode')
      self._alert = kwargs.get(self.hue_noun).get('alert')
      self._bri = kwargs.get(self.hue_noun).get('bri')
      self._reachable = kwargs.get(self.hue_noun).get('reachable')
      self._ct = kwargs.get(self.hue_noun).get('ct')
    self._level = int(self._bri / 255.0 * 100.0)

  def off(self, **kwargs):
    self.setLight({'on': False})
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self.setLight({'on': True})
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self._on

  def get_level(self, **kwargs):
    return self._level

  def set_level(self, **kwargs):
    try:
      level = int(kwargs.get(LEVEL))
    except:
      logging.error('UNKNOWN VALUE PASSED FOR LEVEL')
      return False
    if level is None:
      return False
    return self.setLight({'level': level})

  @property
  def state(self):
    return self._on

  @property
  def hue_noun(self):
    return self._hue_noun

  def setLight(self, value):
    hue_value = {}

    ## END FADE IF SET COMMAND IS GIVEN
    # if value.get('ctfade') is None:
    #  global ctFade
    #  ctFade.endRun()

    # XY
    xy = value.get('xy')
    if xy:
      hue_value.update({'xy': xy})
      self._xy = xy

    # HUE
    hue = value.get('hue')
    if hue:
      hue_value.update({'hue': hue})
      self._hue = hue

    # TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime:
      hue_value.update({'transitiontime': transitiontime})

    ## NAME COLOR
    # name = value.get('name')
    # if name:
    #  value['hex'] = name_to_hex(name)

    # HEX COLOR
    hexColor = value.get('hex')
    if hexColor:
      hue_value.update(self.hexColor(hexColor))

    ## PRESET
    # preset = value.get('preset')
    # if preset:
    #  if preset in PRESETS_CT:
    #    value['ct'] = PRESETS_CT.get(preset)

    # SET FOR LEVEL
    level = value.get('level')
    if level:
      if level > 0:
        if level > 100:
          level = 100
        level = 100 if level >= 100 else level
        bri = int(255.0 / 100.0 * level)
        self._bri = bri
        level = level
        hue_value.update({'bri': bri})
      if level <= 0:
        bri = 0
        level = 0
        self._on = False
        hue_value.update({'bri': bri, 'on': False})
        self._bri = bri
      self._level = level

    # SET FOR BRI
    bri = value.get('bri')
    if bri:
      if bri > 255:
        bri = 255
        self._level = int(bri / 255.0 * 100.0)
      if bri <= 0:
        bri = 0
        self._level = 0
        self._on = False
        hue_value.update({'on': False})
      hue_value.update({'bri': bri})
      self._bri = bri

    # SET CT:
    ct = value.get('ct')
    if ct:
      if 'K' in ct.upper():
        ct = int(ct.upper().replace('K', ''))
        ct = int(1000000 / ct)
      if ct > 500:
        ct = 500
      if ct < 153:
        ct = 153

      hue_value.update({'ct': ct})
      self._ct = ct

    # EFFECT
    effect = value.get('effect')
    if effect:
      hue_value.update({'effect': effect})
      self._effect = effect

    # ALERT
    alert = value.get('alert')
    if alert:
      hue_value.update({'alert': alert})
      self._alert = alert

    # SET FOR ON
    on = value.get('on')
    if on is not None:
      if on:
        hue_value.update({'on': on})
      else:
        hue_value.update({'on': on, 'bri': 255})
      self._on = on

    # Turn lights on unless told not to or has already been set
    if hue_value.get('on') is None and not value.get('onOn'):
      hue_value.update({'on': True})
      self._on = True

    self.set_hue_device(hue_value)
    return value

  # TODO: Bringe CT Fade back in
  # def ctFade(self, args={}):
  #  global ctFade
  #  ctFade = CTFade(str(self._id), args.get('startK'), args.get('endK'), args.get('fadeS'), args.get('startL'),
  #                  args.get('endL'))

  def switch(self, value):
    if value == 'on':
      self.setLight({'on': True})
    elif value == 'off':
      self.setLight({'on': False})

  def set_hue_device(self, value):
    path = '%ss/%s/%s' % (self._hue_type, self._hue_number, self._hue_noun)
    command = Command(self._hue_service, self.id, 'send_request', **{'path': path, 'data': value, 'method': 'PUT'})
    self.firefly.send_command(command)

  def hexColor(self, colorHex):
    if '#' in colorHex:
      colorHex = colorHex.replace('#', '')
    if 'LST' in self._modelid:
      # TODO: Fix this
      return colorHex
      #  return {'xy': converter.hexToCIE1931(colorHex, lightType='LST')}
      # return {'xy': converter.hexToCIE1931(colorHex)}