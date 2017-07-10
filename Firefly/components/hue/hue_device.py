from Firefly import logging
# from rgb_cie import Converter
from Firefly.components.hue.ct_fade import CTFade
from Firefly.components.virtual_devices import AUTHOR
from Firefly.const import (ACTION_LEVEL, ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ALEXA_OFF, ALEXA_ON, ALEXA_SET_COLOR,
                           ALEXA_SET_COLOR_TEMP, ALEXA_SET_PERCENTAGE, COMMAND_SET_LIGHT, COMMAND_UPDATE,
                           DEVICE_TYPE_COLOR_LIGHT, EVENT_ACTION_OFF, EVENT_ACTION_ON, LEVEL, STATE, SWITCH)
from Firefly.helpers.device import Device
from Firefly.helpers.events import Command
from Firefly.helpers.metadata import metaDimmer, metaSwitch

TITLE = 'Firefly Hue Device'
DEVICE_TYPE = DEVICE_TYPE_COLOR_LIGHT
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL, COMMAND_SET_LIGHT, 'ct_fade']
INITIAL_VALUES = {
  '_state':            EVENT_ACTION_OFF,
  '_uniqueid':         '-1',
  '_manufacturername': 'unknown',
  '_on':               False,
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
    else:
      # TODO: Remove hacky logic
      # INITIAL_VALUES.update(kwargs['initial_values'])
      kwargs['initial_values'] = INITIAL_VALUES
    if commands:
      c = set(commands)
      c.update(COMMANDS)
      commands = list(c)
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
    self.add_command(COMMAND_SET_LIGHT, self.setLight)
    self.add_command('ct_fade', self.set_ct_fade)

    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

    self.add_request(STATE, self.get_state)
    self.add_request(SWITCH, self.get_state)

    self.add_request('hue', self.get_hue)
    self.add_request('sat', self.get_sat)

    self.add_action(STATE, metaSwitch(primary=True))
    self.add_action(LEVEL, metaDimmer())

    self.add_alexa_action(ALEXA_OFF)
    self.add_alexa_action(ALEXA_ON)
    self.add_alexa_action(ALEXA_SET_PERCENTAGE)
    self.add_alexa_action(ALEXA_SET_COLOR_TEMP)
    self.add_alexa_action(ALEXA_SET_COLOR)

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_COLOR_LIGHT', STATE)

    self._hue_noun = 'state' if self._package == 'Firefly.components.hue.hue_light' else 'action'

    if self._hue_noun == 'state':
      self._hue_type = 'light'
    else:
      self._hue_type = 'group'
    self._hue_number = kwargs.get('hue_number')

    self._name = kwargs.get('name')
    self._uniqueid = kwargs.get('uniqueid', '-1')
    self._manufacturername = kwargs.get('manufacturername', '')
    self._swversion = kwargs.get('swversion', '')
    self._modelid = kwargs.get('modelid', '')
    self._bri = 0
    self._ct_fade = None


    if kwargs.get(self.hue_noun):
      self._on = kwargs.get(self.hue_noun).get('on', False)
      self._hue = kwargs.get(self.hue_noun).get('hue', 0)
      self._sat = kwargs.get(self.hue_noun).get('sat', 0)
      self._effect = kwargs.get(self.hue_noun).get('effect', '')
      self._xy = kwargs.get(self.hue_noun).get('xy', 0)
      self._colormode = kwargs.get(self.hue_noun).get('colormode', '')
      self._alert = kwargs.get(self.hue_noun).get('alert', False)
      self._bri = kwargs.get(self.hue_noun).get('bri', 0)
      self._reachable = kwargs.get(self.hue_noun).get('reachable', '-1')
      self._ct = kwargs.get(self.hue_noun).get('ct', 0)

    self._level = int(self._bri / 255.0 * 100.0)

  def update(self, **kwargs):
    self._name = kwargs.get('name')
    self._uniqueid = kwargs.get('uniqueid', '')
    self._manufacturername = kwargs.get('manufacturername', '')
    self._swversion = kwargs.get('swversion', '')
    self._modelid = kwargs.get('modelid', '')
    self._hue_service = kwargs.get('hue_service', 'service_hue')
    self._hue_number = kwargs.get('hue_number')

    if self._alias != self._name:
      self._alias = self._name
      self.firefly.aliases.set_alias(self.id, self._alias)

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
    self.setLight(on=False)
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self.setLight(on=True)
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def get_level(self, **kwargs):
    return self._level

  def get_sat(self, **kwargs):
    return self._sat

  def get_hue(self, **kwargs):
    return self._hue

  def set_level(self, **kwargs):
    try:
      level = int(kwargs.get(LEVEL))
    except:
      logging.error(code='FF.HUE.SET.001')  # unknown value passed for level
      return False
    if level is None:
      return False
    return self.setLight(level=level)

  @property
  def state(self):
    return EVENT_ACTION_ON if self._on else EVENT_ACTION_OFF

  @property
  def hue_noun(self):
    return self._hue_noun

  def setLight(self, **kwargs):
    value = kwargs
    hue_value = {}

    # END FADE IF SET COMMAND IS GIVEN
    if not value.get('ct_fade', False):
      if self._ct_fade is not None:
        self._ct_fade.endRun()
      self._ct_fade = None

    # XY
    xy = value.get('xy')
    if xy is not None:
      hue_value.update({
        'xy': xy
      })
      self._xy = xy

    # HUE
    hue = value.get('hue')
    if hue is not None:
      hue_value.update({
        'hue': hue
      })
      self._hue = hue

    # TRANS TIME
    transitiontime = value.get('transitiontime')
    if transitiontime is not None:
      try:
        transitiontime = int(transitiontime)
      except:
        transitiontime = 40
      hue_value.update({
        'transitiontime': transitiontime
      })

    ## NAME COLOR
    # name = value.get('name')
    # if name:
    #  value['hex'] = name_to_hex(name)

    # HEX COLOR
    hexColor = value.get('hex')
    if hexColor is not None:
      hue_value.update(self.hexColor(hexColor))

    ## PRESET
    # preset = value.get('preset')
    # if preset:
    #  if preset in PRESETS_CT:
    #    value['ct'] = PRESETS_CT.get(preset)

    # SET FOR LEVEL
    level = value.get('level')
    if level is not None:
      try:
        level = int(level)
      except:
        level = 100

      if level > 0:
        level = min(level, 100)
        bri = int(255.0 / 100.0 * level)
        self._bri = bri
        self._on = True
        hue_value.update({
          'bri': bri,
          'on': True
        })
      else:
        bri = 0
        level = 0
        self._on = False
        hue_value.update({
          'bri': bri,
          'on':  False
        })
        self._bri = bri
      self._level = level

    # SET FOR BRI
    bri = value.get('bri')
    if bri is not None:
      bri = min(bri, 255)
      if bri <= 0:
        bri = 0
        self._level = 0
        self._on = False
        hue_value.update({
          'on': False
        })
      else:
        self._on = True
        self._level = int(bri / 255.0 * 100.0)
      hue_value.update({
        'bri': bri,
        'on': True
      })
      self._bri = bri

    # SET CT:
    ct = value.get('ct')
    if ct is not None:
      ct = check_ct(ct)
      hue_value.update({
        'ct': ct
      })
      self._ct = ct

    # SET SAT:
    sat = value.get('sat')
    if sat is not None:
      try:
        sat = int(sat)
        sat = min(sat, 255)
        sat = max(sat, 0)
        hue_value.update({
          'sat': sat
        })
      except:
        pass

    # EFFECT
    effect = value.get('effect')
    if effect is not None:
      hue_value.update({
        'effect': effect
      })
      self._effect = effect

    # ALERT
    alert = value.get('alert')
    if alert is not None:
      hue_value.update({
        'alert': alert
      })
      self._alert = alert

    # SET FOR ON
    on = value.get('on')
    if on is not None:
      if on:
        hue_value.update({
          'on': on
        })
      else:
        hue_value.update({
          'on':  on
        })
      self._on = on

    # Turn lights on unless told not to or has already been set
    if hue_value.get('on') is None and not value.get('no_on'):
      hue_value.update({
        'on': True
      })
      self._on = True

    # Process special values from alexa
    alexa = value.get('alexa')
    if alexa is not None:
      hue = int(65535 / 360 * alexa.get('hue', 0))
      sat = int(alexa.get('sat', 0) * 254)
      bri = int(alexa.get('bri', 0) * 254)

      hue_value = {
        'hue': hue,
        'bri': bri,
        'sat': sat
      }

    self.set_hue_device(hue_value)
    return value

  def set_ct_fade(self, **kwargs):
    """
    Set color temperature fade over time.
    
    Args:
      start_k: (str) Start color temp in k (2700k)
      end_k: (str) End color temp in k (2700k)
      start_level: (int) Start level
      end_level: (int) End Level

    Returns:
      None

    """
    start_k = kwargs.get('start_k')
    end_k = kwargs.get('end_k')
    start_level = kwargs.get('start_level')
    end_level = kwargs.get('end_level')

    try:
      if 'K' in start_k.upper():
        start_k = int(start_k.upper().replace('K', ''))
      if 'K' in end_k.upper():
        end_k = int(end_k.upper().replace('K', ''))
      start_k = min(start_k, 6500)
      start_k = max(start_k, 2000)
      end_k = min(end_k, 6500)
      end_k = max(end_k, 2000)

      fade_sec = int(kwargs.get('fade_sec', 1500))
      if start_level is not None and end_level is not None:
        start_level = int(start_level)
        end_level = int(end_level)

    except:
      logging.error(code='FF.HUE.SET.002')  # error parsing ct_fade
      return

    self._ct_fade = CTFade(self._firefly, str(self.id), start_k, end_k, fade_sec, start_level, end_level)

  def switch(self, value):
    if value == 'on':
      self.setLight(on=True)
    elif value == 'off':
      self.setLight(on=False)

  def set_hue_device(self, value):
    path = '%ss/%s/%s' % (self._hue_type, self._hue_number, self._hue_noun)
    command = Command(self._hue_service, self.id, 'send_request', **{
      'path':   path,
      'data':   value,
      'method': 'PUT'
    })
    self.firefly.send_command(command)

  def hexColor(self, colorHex):
    if '#' in colorHex:
      colorHex = colorHex.replace('#', '')
    if 'LST' in self._modelid:
      # TODO: Fix this
      return colorHex
      #  return {'xy': converter.hexToCIE1931(colorHex, lightType='LST')}
      # return {'xy': converter.hexToCIE1931(colorHex)}


def check_ct(ct) -> int:
  if 'K' in ct.upper():
    try:
      ct = int(ct.upper().replace('K', ''))
    except:
      ct = 2700
    ct = 1000000.0 / ct
  else:
    try:
      ct = int(ct)
    except:
      ct = 1000000.0 / 2700.0

  if ct > 500:
    ct = 500
  if ct < 153:
    ct = 153

  return int(ct)
