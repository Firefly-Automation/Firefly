from Firefly import logging
from Firefly.const import ACTION_OFF, ACTION_ON, ALEXA_OFF, ALEXA_ON, ALEXA_SET_PERCENTAGE, COMMAND_SET_LIGHT, DEVICE_TYPE_SWITCH, LEVEL, SWITCH
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device

from Firefly.helpers.metadata import action_on_off_switch, metaSlider, action_dimmer

from Firefly.services.alexa.alexa_const import ALEXA_LIGHT, ALEXA_POWER_INTERFACE, ALEXA_POWER_LEVEL_INTERFACE

ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL, COMMAND_SET_LIGHT]

REQUESTS = [SWITCH, LEVEL]

CAPABILITIES = {
  LEVEL:             False,
  SWITCH:            False,
  COMMAND_SET_LIGHT: True
}

INITIAL_VALUES = {
  '_level':     -1,
  '_switch':    ACTION_OFF,
  '_min_level': -1,
}


class Light(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_SWITCH, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP SWITCH')

    INITIAL_VALUES.update(initial_values)
    initial_values = INITIAL_VALUES

    CAPABILITIES.update(capabilities)
    capabilities = CAPABILITIES

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    self.add_alexa_categories(ALEXA_LIGHT)

    if capabilities[SWITCH] and SWITCH in requests and ACTION_OFF in commands and ACTION_ON in commands:
      self.add_command(ACTION_OFF, self.set_off)
      self.add_command(ACTION_ON, self.set_on)
      self.add_request(SWITCH, self.get_switch)

      self.add_alexa_capabilities(ALEXA_POWER_INTERFACE)

      self.add_action(SWITCH, action_on_off_switch())

    if capabilities[LEVEL] and LEVEL in requests and LEVEL in commands:
      self.add_request(LEVEL, self.get_level)
      self.add_command(LEVEL, self.set_level)

      self.add_action(LEVEL, action_dimmer())
      self.add_alexa_capabilities(ALEXA_POWER_LEVEL_INTERFACE)

    if capabilities[COMMAND_SET_LIGHT] and COMMAND_SET_LIGHT in commands:
      self.add_command(COMMAND_SET_LIGHT, self.set_light)

    self._alexa_export = True

    self.capabilities = CAPABILITIES

  def update_values(self, level=None, switch=None, **kwargs):
    if switch is not None:
      if type(switch) is bool:
        self._switch = ACTION_ON if switch else ACTION_OFF
      if type(switch) is int:
        if switch == 0:
          self._switch = ACTION_OFF
        else:
          self._switch = ACTION_ON
      else:
        self._switch = switch

    if level is not None:
      if type(level) is not int:
        self._level = -1

      # Fix rounding errors for 100%
      if level == 99:
        level = 100

      self._level = level

  def get_switch(self, **kwargs):
    return self._switch

  def get_level(self, **kwargs):
    return self._level

  def set_level(self, level=-1, **kwargs):
    logging.error('set_level not implemented.')

  def set_switch(self, switch=None, **kwargs):
    logging.error('set_switch not implemented.')

  def set_light(self, **kwargs):
    logging.error('set_light not implemented.')

  def set_on(self, **kwargs):
    return self.set_switch(ACTION_ON)

  def set_off(self, **kwargs):
    return self.set_switch(ACTION_OFF)
