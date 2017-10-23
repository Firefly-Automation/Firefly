from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import AUTHOR, LUX, MOTION
from Firefly.helpers.device_types.multi_sensor import MultiSensor

BATTERY = 'battery'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
ALARM = 'alarm'
DEVICE_TYPE_MULTI_SENSOR = 'multi_sensor'
ULTRAVIOLET = 'ultraviolet'

CAPABILITIES = {
  ALARM:       True,
  BATTERY:     True,
  HUMIDITY:    True,
  LUX:         True,
  MOTION:      True,
  TEMPERATURE: True,
  ULTRAVIOLET: True
}

COMMANDS = []

REQUESTS = [MOTION, ALARM, LUX, TEMPERATURE, HUMIDITY, ULTRAVIOLET, BATTERY]


class ZwaveMultiSensor(MultiSensor, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Multi Sensor', initial_values={}, **kwargs):
    logging.message('SETTING UP ZWAVE MULTI SENSOR')
    if kwargs.get('commands'):
      commands = kwargs.get('commands')
      kwargs.pop('commands')
    else:
      commands = COMMANDS

    if kwargs.get('requests'):
      requests = kwargs.get('requests')
      kwargs.pop('requests')
    else:
      requests = REQUESTS

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_MULTI_SENSOR, capabilities=CAPABILITIES, initial_values=initial_values, **kwargs)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    self._node = node

    super().update_from_zwave(node, **kwargs)

    if values is None:
      logging.message('ZWAVE MULTI SENSOR NO VALUES GIVEN')
      return

    label = values.label
    if label == 'Sensor':
      self.update_values(motion=values.data)
    if label == 'Battery Level':
      self.update_values(battery=values.data)
    if label == 'Burglar':
      self.update_values(alarm=values.data)
    if label == 'Temperature':
      self.update_values(temperature=values.data)
    if label == 'Luminance':
      self.update_values(lux=values.data)
    if label == 'Relative Humidity':
      self.update_values(humidity=values.data)
    if label == 'Ultraviolet':
      self.update_values(ultraviolet=values.data)
