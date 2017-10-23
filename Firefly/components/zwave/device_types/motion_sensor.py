from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import AUTHOR, DEVICE_TYPE_MOTION, LUX, MOTION
from Firefly.helpers.device_types.multi_sensor import MultiSensor

BATTERY = 'battery'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
ALARM = 'alarm'
ULTRAVIOLET = 'ultraviolet'

CAPABILITIES = {
  ALARM:       True,
  BATTERY:     True,
  HUMIDITY:    False,
  LUX:         False,
  MOTION:      True,
  TEMPERATURE: False,
  ULTRAVIOLET: False
}

COMMANDS = []

REQUESTS = [MOTION, ALARM, BATTERY]


class ZwaveMotionSensor(MultiSensor, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Motion Sensor', initial_values={}, **kwargs):
    if kwargs.get('commands') is not None:
      commands = kwargs.get('commands')
      kwargs.pop('commands')
    else:
      commands = COMMANDS

    if kwargs.get('requests') is not None:
      requests = kwargs.get('requests')
      kwargs.pop('requests')
    else:
      requests = REQUESTS

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_MOTION, capabilities=CAPABILITIES, initial_values=initial_values, **kwargs)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    self._node = node

    super().update_from_zwave(node, **kwargs)

    if values is None:
      logging.message('ZWAVE MOTION SENSOR NO VALUES GIVEN')
      return

    label = values.label
    if label == 'Sensor':
      self.update_values(motion=values.data)
    if label == 'Battery Level':
      self.update_values(battery=values.data)
    if label == 'Burglar':
      self.update_values(alarm=values.data)
