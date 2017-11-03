from Firefly import logging
from Firefly.const import ACTION_OFF, ACTION_ON, COMMAND_SET_LIGHT, DEVICE_TYPE_SWITCH, LEVEL, SWITCH
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata import action_battery, action_dimmer, action_on_off_switch, action_text

from Firefly.services.alexa.alexa_const import ALEXA_POWER_INTERFACE, ALEXA_POWER_LEVEL_INTERFACE, ALEXA_SWITCH

ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL]

REQUESTS = [ALARM, BATTERY, SWITCH, CURRENT, VOLTAGE, WATTS, LEVEL, COMMAND_SET_LIGHT]

CAPABILITIES = {
  ALARM:       False,
  BATTERY:     False,
  LEVEL:       False,
  POWER_METER: False,
  SWITCH:      True,
}

INITIAL_VALUES = {
  '_alarm':                   False,
  '_battery':                 -1,
  '_current':                 -1,
  '_current_energy_reading':  -1,
  '_level':                   -1,
  '_previous_energy_reading': -1,
  '_switch':                  ACTION_OFF,
  '_voltage':                 -1,
  '_watts':                   -1,
  '_min_level':               -1,
}


class Switch(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_SWITCH, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP SWITCH')

    INITIAL_VALUES.update(initial_values)
    initial_values = INITIAL_VALUES

    CAPABILITIES.update(capabilities)
    capabilities = CAPABILITIES

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    self.add_alexa_categories(ALEXA_SWITCH)
    self.add_command(COMMAND_SET_LIGHT, self.set_light)

    if capabilities[ALARM] and ALARM in requests:
      self.add_request(ALARM, self.get_alarm)
      self.add_action(ALARM, action_text(title='Alarm', request=ALARM))

    if capabilities[BATTERY] and BATTERY in requests:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_battery())

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

    if capabilities[POWER_METER]:
      if VOLTAGE in requests:
        self.add_request(VOLTAGE, self.get_voltage)
        self.add_action(VOLTAGE, action_text(title='Current Voltage', request=VOLTAGE))

      if CURRENT in requests:
        self.add_request(CURRENT, self.get_power_current)
        self.add_action(CURRENT, action_text(title='Power Current', request=CURRENT))

      if WATTS in requests:
        self.add_request(WATTS, self.get_watts)
        self.add_action(WATTS, action_text(title='Watts', request=WATTS))

        # TODO: Add functions for energy readings.

    self._alexa_export = True

    self.capabilities = CAPABILITIES

  def update_values(self, alarm=None, battery=None, voltage=None, power_current=None, watts=None, level=None, switch=None, previous_energy_reading=None, current_energy_reading=None, **kwargs):

    if alarm is not None:
      self._alarm = alarm

    if battery is not None:
      self._battery = battery

    if voltage is not None:
      self._voltage = voltage

    if power_current is not None:
      self._current = power_current

    if watts is not None:
      self._watts = watts

    if switch is not None:
      if type(switch) is bool:
        self._switch = ACTION_ON if switch else ACTION_OFF
      else:
        self._switch = switch

    if level is not None:
      if type(level) is not int:
        self._level = -1

      # Fix rounding errors for 100%
      if level == 99:
        level = 100

      self._level = level

    if previous_energy_reading is not None:
      self._previous_energy_reading = previous_energy_reading

    if current_energy_reading is not None:
      self._current_energy_reading = current_energy_reading

  def get_battery(self, **kwargs):
    return self._battery

  def get_switch(self, **kwargs):
    return self._switch

  def get_level(self, **kwargs):
    return self._level

  def set_level(self, level=-1, **kwargs):
    logging.error('set_level not implemented.')

  def set_light(self, **kwargs):
    if SWITCH in kwargs:
      self.set_switch(**kwargs)
    if LEVEL in kwargs:
      self.set_level(**kwargs)

  def set_switch(self, switch=None, **kwargs):
    logging.error('set_switch not implemented.')

  def set_on(self, **kwargs):
    return self.set_switch(ACTION_ON)

  def set_off(self, **kwargs):
    return self.set_switch(ACTION_OFF)

  def get_alarm(self, **kwargs):
    return self._alarm

  def get_voltage(self, **kwargs):
    return self._voltage

  def get_power_current(self, **kwargs):
    return self._current

  def get_watts(self, **kwargs):
    return self._watts
