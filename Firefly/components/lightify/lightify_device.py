from Firefly.const import AUTHOR, ACTION_OFF, ACTION_ON, EVENT_ACTION_ON, EVENT_ACTION_OFF, STATE, COMMAND_SET_LIGHT, COMMAND_UPDATE, ACTION_LEVEL, LEVEL, ALEXA_OFF, ALEXA_ON, ALEXA_SET_PERCENTAGE, SWITCH
from Firefly.helpers.metadata import metaSwitch, metaDimmer, action_on_off_switch
from Firefly.helpers.device import Device
from lightify import Luminary
from Firefly import logging

TITLE = 'Lightify Device'
COMMANDS = [EVENT_ACTION_ON, EVENT_ACTION_OFF, ACTION_LEVEL, COMMAND_UPDATE]
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_level': 0
}

class LightifyDevice(Device):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):
    if not kwargs.get('initial_values'):
      kwargs['initial_values'] = INITIAL_VALUES
    else:
      INITIAL_VALUES.update(kwargs['initial_values'])
      kwargs['initial_values'] = INITIAL_VALUES
    if commands:
      c = set(commands)
      c.update(COMMANDS)
      commands = list(c)
    super().__init__(firefly, package, title, author, commands, requests, device_type, **kwargs)

    self.add_command(EVENT_ACTION_OFF, self.off)
    self.add_command(EVENT_ACTION_ON, self.on)
    self.add_command(ACTION_LEVEL, self.level)
    self.add_command(COMMAND_SET_LIGHT, self.set_light)
    self.add_command(COMMAND_UPDATE, self.update_lightify)

    self.add_request(SWITCH, self.get_state)
    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

    self.add_action(SWITCH, action_on_off_switch())
    self.add_action(LEVEL, metaDimmer())

    self.add_alexa_action(ALEXA_OFF)
    self.add_alexa_action(ALEXA_ON)
    self.add_alexa_action(ALEXA_SET_PERCENTAGE)
    #self.add_alexa_action(ALEXA_SET_COLOR_TEMP)
    #self.add_alexa_action(ALEXA_SET_COLOR)

    self.lightify_object:Luminary = kwargs.get('lightify_object')
    self.lightify_type = kwargs.get('lightify_type')

    self._export_ui = kwargs.get('export_ui', True)

  def on(self, **kwargs):
    self._state = EVENT_ACTION_ON
    self.lightify_object.set_onoff(True)

  def off(self, **kwargs):
    self._state = EVENT_ACTION_OFF
    self.lightify_object.set_onoff(False)

  def level(self, **kwargs):
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
    self._level = level

  def set_light(self, **kwargs):
    if kwargs.get(LEVEL):
      self.level(**kwargs)


  def get_level(self, **kwargs):
    return self._level

  def get_state(self, **kwargs):
    return self._state

  def update_lightify(self, **kwargs):
    pass