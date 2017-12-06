from Firefly import logging
from Firefly.const import LUX, MOTION, MOTION_ACTIVE, MOTION_INACTIVE
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata.metadata import action_motion, action_text

# TODO: Add support for temp reporting.
# from Firefly.services.alexa.alexa_const import ALEXA_TEMPERATURE_SENSOR, ALEXA_TEMPERATURE_INTERFACE

BATTERY = 'battery'
ALARM = 'alarm'
DEVICE_TYPE_MULTI_SENSOR = 'multi_sensor'

COMMANDS = []

REQUESTS = [ALARM, BATTERY, HUMIDITY, LUX, MOTION, TEMPERATURE, ULTRAVIOLET]

CAPABILITIES = {
  ALARM:       False,
  BATTERY:     False,
  HUMIDITY:    False,
  LUX:         False,
  MOTION:      False,
  TEMPERATURE: False,
  ULTRAVIOLET: False
}

INITIAL_VALUES = {
  '_alarm':       False,
  '_battery':     -1,
  '_humidity':    -1,
  '_lux':         -1,
  '_motion':      MOTION_INACTIVE,
  '_temperature': -1,
  '_ultraviolet': -1
}


class MultiSensor(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_MULTI_SENSOR, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP MULTI_SENSOR')

    initial_values_updated = INITIAL_VALUES.copy()
    initial_values_updated.update(initial_values)
    initial_values = initial_values_updated

    capabilities_updated = CAPABILITIES.copy()
    capabilities_updated.update(capabilities)
    capabilities = capabilities_updated

    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    if capabilities[ALARM] and ALARM in requests:
      self.add_request(ALARM, self.get_alarm)
      self.add_action(ALARM, action_text(title='Alarm Code', context='Alarm code from device', request=ALARM))

    if capabilities[BATTERY] and BATTERY in requests:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_text(title='Battery', context='Battery Level', request=BATTERY, units='%'))

    if capabilities[HUMIDITY] and HUMIDITY in requests:
      self.add_request(HUMIDITY, self.get_humidity)
      self.add_action(HUMIDITY, action_text(title='Humidity Level', context='Humidity %', request=HUMIDITY, units='%'))

    if capabilities[LUX] and LUX in requests:
      self.add_request(LUX, self.get_lux)
      self.add_action(LUX, action_text(title='Lux Level', request=LUX, units='lux'))

    if capabilities[MOTION] and MOTION in requests:
      self.add_request(MOTION, self.get_motion)
      self.add_action(MOTION, action_motion(primary=True))
      if 'motion' not in self.tags:
        self._tags.append('motion')

    if capabilities[TEMPERATURE] and TEMPERATURE in requests:
      self.add_request(TEMPERATURE, self.get_temperature)
      self.add_action(TEMPERATURE, action_text(title='Temperature', request=TEMPERATURE, units='F'))

    if capabilities[ULTRAVIOLET] and ULTRAVIOLET in requests:
      self.add_request(ULTRAVIOLET, self.get_ultraviolet)
      self.add_action(ULTRAVIOLET, action_text(title='Ultraviolet', request=ULTRAVIOLET))

    self._alexa_export = False
    self.capabilities = capabilities

    # TODO: Use device settings for this
    self._security_monitoring = kwargs.get('security_monitoring', True)

  def update_values(self, alarm=None, battery=None, humidity=None, lux=None, motion=None, temperature=None, ultraviolet=None, **kwargs):
    if alarm is not None:
      self._alarm = alarm
    if battery is not None:
      self._battery = battery
    if humidity is not None:
      self._humidity = humidity
    if lux is not None:
      self._lux = lux
    if motion is not None:
      if type(motion) is str:
        self._motion = motion
      if type(motion) is bool:
        self._motion = MOTION_ACTIVE if motion else MOTION_INACTIVE
    if temperature is not None:
      self._temperature = temperature
    if ultraviolet is not None:
      self._ultraviolet = ultraviolet

  def get_battery(self, **kwargs):
    return self._battery

  def get_motion(self, **kwargs):
    return self._motion

  def get_lux(self, **kwargs):
    return self._lux

  def get_temperature(self, **kwargs):
    return self._temperature

  def get_alarm(self, **kwargs):
    return self._alarm

  def get_humidity(self, **kwargs):
    return self._humidity

  def get_ultraviolet(self, **kwargs):
    return self._ultraviolet
