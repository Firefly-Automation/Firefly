from lightify import Luminary

from Firefly import logging
from Firefly.const import ACTION_LEVEL, AUTHOR, COMMAND_UPDATE, EVENT_ACTION_OFF, EVENT_ACTION_ON, LEVEL, SWITCH, COMMAND_SET_LIGHT
from Firefly.helpers.device_types.light import Light

TITLE = 'Lightify Device'
COMMANDS = [EVENT_ACTION_ON, EVENT_ACTION_OFF, ACTION_LEVEL, COMMAND_UPDATE, COMMAND_SET_LIGHT]
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_level': 0
}

CAPABILITIES = {
  LEVEL:  True,
  SWITCH: True,
  COMMAND_SET_LIGHT: True
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

  def set_on(self, **kwargs):
    self.lightify_object.set_onoff(True)
    self.update_values(switch=True)

  def set_off(self, **kwargs):
    self.lightify_object.set_onoff(False)
    self.update_values(switch=False)

  def set_level(self, **kwargs):
    level = kwargs.get('level')
    if level is None:
      return
    try:
      level = int(level)
    except:
      logging.error('error parsing level')
      return
    # TODO: Parse timing info
    self.lightify_object.set_luminance(level, 4)
    self.update_values(level=level)

  def set_light(self, **kwargs):
    if kwargs.get(LEVEL):
      self.set_level(**kwargs)

  def update_lightify(self, **kwargs):
    pass
