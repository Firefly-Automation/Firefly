from Firefly import logging
from Firefly.const import DEVICE_TYPE_WATER_SENSOR, SENSOR_DRY, SENSOR_WET, WATER
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata.metadata import action_text, action_water_dry


ALARM = 'alarm'

COMMANDS = []

REQUESTS = [ALARM, BATTERY, WATER]

CAPABILITIES = {
  ALARM:   False,
  BATTERY: False,
  WATER:   False,
}

INITIAL_VALUES = {
  '_alarm':   False,
  '_battery': -1,
  '_water':   SENSOR_DRY
}


class WaterSensor(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_WATER_SENSOR, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP MULTI_SENSOR')
    INITIAL_VALUES.update(initial_values)
    initial_values = INITIAL_VALUES
    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    if capabilities[ALARM] and ALARM in requests:
      self.add_request(ALARM, self.get_alarm)
      self.add_action(ALARM, action_text(title='Alarm Code', context='Alarm code from device', request=ALARM))

    if capabilities[BATTERY] and BATTERY in requests:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_text(title='Battery', context='Battery Level', request=BATTERY))

    if capabilities[WATER] and WATER in requests:
      self.add_request(WATER, self.get_water)
      self.add_action(WATER, action_water_dry(primary=True))
      if 'water' not in self.tags:
        self._tags.append('water')

    self._alexa_export = False
    self.capabilities = CAPABILITIES

    # TODO: Use device settings for this
    self._security_monitoring = kwargs.get('security_monitoring', True)

  def update_values(self, alarm=None, battery=None, water=None, **kwargs):
    if alarm is not None:
      self._alarm = alarm
    if battery is not None:
      self._battery = battery
    if water is not None:
      if type(water) is str:
        self._water = water
      if type(water) is bool:
        self._water = SENSOR_WET if water else SENSOR_DRY

  def get_battery(self, **kwargs):
    return self._battery

  def get_water(self, **kwargs):
    return self._water

  def get_alarm(self, **kwargs):
    return self._alarm
