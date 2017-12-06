from lightify import Luminary

from Firefly import logging
from Firefly.const import ACTION_LEVEL, AUTHOR, COMMAND_SET_LIGHT, COMMAND_UPDATE, EVENT_ACTION_OFF, EVENT_ACTION_ON, LEVEL, SWITCH, ACTION_ON, ACTION_OFF
from Firefly.helpers.device import COLOR, COLOR_TEMPERATURE
from Firefly.helpers.device_types.light import Light
from Firefly.util.color import Colors, check_ct

TITLE = 'Lightify Device'
COMMANDS = [EVENT_ACTION_ON, EVENT_ACTION_OFF, ACTION_LEVEL, COMMAND_UPDATE, COMMAND_SET_LIGHT]
INITIAL_VALUES = {
  '_state':            EVENT_ACTION_OFF,
  '_manufacturername': 'lightify',
  '_on':               False,
  '_switch':           'off',
  '_hue':              0,
  '_sat':              0,
  '_bri':              0,
  '_reachable':        False,
  '_type':             'unknown',
  '_ct':               0,
  '_level':            0,
  '_transition_time': 20
}

CAPABILITIES = {
  LEVEL:             True,
  SWITCH:            True,
  COLOR_TEMPERATURE: True,
  COLOR:             True
}

REQUESTS = [SWITCH, LEVEL]


class LightifyDevice(Light):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, AUTHOR, capabilities=CAPABILITIES, **kwargs)
    self.add_command(COMMAND_UPDATE, self.update_lightify)

    self.lightify_object: Luminary = kwargs.get('lightify_object')
    self.lightify_type = kwargs.get('lightify_type')

    self._export_ui = kwargs.get('export_ui', True)


  def set_light(self, switch=None, level=None, colors=Colors(), ct=None, **kwargs):
    if switch is not None:
      self.lightify_object.set_onoff(switch == ACTION_ON)
      self.update_values(switch=switch)

    if level is not None:
      self.lightify_object.set_luminance(level, self._transition_time)
      self.update_values(level=level)

    if colors.is_set:
      self.lightify_object.set_rgb(colors.r, colors.g, colors.b, self._transition_time)
      self.update_values(r=colors.r, g=colors.g, b=colors.b)

    if ct is not None:
      ct = check_ct(ct)
      self.lightify_object.set_temperature(ct, self._transition_time)
      self.update_values(ct=ct)

  def update_lightify(self, **kwargs):
    pass
