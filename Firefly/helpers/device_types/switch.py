from Firefly import logging
from Firefly.const import ACTION_OFF, ACTION_ON, ALEXA_OFF, ALEXA_ON, ALEXA_SET_PERCENTAGE, DEVICE_TYPE_SWITCH, LEVEL, STATE, SWITCH
from Firefly.helpers.device import Device
from Firefly.helpers.metadata import action_on_off_switch, action_text, metaSlider, metaSwitch, metaText

BATTERY = 'battery'
ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON, LEVEL]

REQUESTS = [ALARM, BATTERY, SWITCH, CURRENT, VOLTAGE, WATTS, LEVEL]

CAPABILITIES = {
  ALARM:       False,
  BATTERY:     False,
  LEVEL:       False,
  POWER_METER: False,
  SWITCH:      False,
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

    # TODO: Remove this when new ui is done
    if STATE not in requests:
      requests.append(STATE)

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    if capabilities[ALARM] and ALARM in requests:
      self.add_request(ALARM, self.get_alarm)
      self.add_action(ALARM, metaText(title='Alarm', text_request=ALARM))

    if capabilities[BATTERY] and BATTERY in requests:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, metaText(title='Battery Level', text_request=BATTERY))

    if capabilities[SWITCH] and SWITCH in requests and ACTION_OFF in commands and ACTION_ON in commands:
      self.add_command(ACTION_OFF, self.set_off)
      self.add_command(ACTION_ON, self.set_on)
      self.add_request(SWITCH, self.get_switch)

      self.add_action('NEW_SWITCH', action_on_off_switch(primary=False))
      self.add_alexa_action(ALEXA_OFF)
      self.add_alexa_action(ALEXA_ON)

      # TODO: Remove this when new ui is done
      self.add_request(STATE, self.get_switch)
      self.add_action(SWITCH, metaSwitch(title='Switch', primary=True, control_type='switch'))

    if capabilities[LEVEL] and LEVEL in requests and LEVEL in commands:
      self.add_request(LEVEL, self.get_level)
      self.add_command(LEVEL, self.set_level)

      self.add_action(LEVEL, metaSlider(title='Set Level', set_command=LEVEL, command_param=LEVEL))
      self.add_alexa_action(ALEXA_SET_PERCENTAGE)

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
