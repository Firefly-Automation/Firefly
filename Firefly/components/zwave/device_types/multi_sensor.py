from Firefly import logging

from Firefly.helpers.device_types.multi_sensor import MultiSensor
from Firefly.components.zwave.zwave_device import ZwaveDevice
from openzwave.network import ZWaveNode
from Firefly.const import MOTION, STATE, LUX, MOTION_INACTIVE, MOTION_ACTIVE, AUTHOR
from openzwave.value import ZWaveValue

BATTERY = 'battery'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
ALARM = 'alarm'
DEVICE_TYPE_MULTI_SENSOR = 'multi_sensor'

CAPABILITIES = {
  ALARM: True,
  BATTERY: True,
  HUMIDITY: True,
  LUX: True,
  MOTION: True,
  TEMPERATURE: True
}

COMMANDS = []
REQUESTS = [
  MOTION,
  ALARM,
  LUX,
  TEMPERATURE,
  HUMIDITY,
  BATTERY
]

class ZwaveMultiSensor(MultiSensor, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Multi Sensor', initial_values={}, **kwargs):
    logging.message('SETTING UP ZWAVE MULTI SENSOR')
    super().__init__(firefly, package, title, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE_MULTI_SENSOR, capabilities=CAPABILITIES, initial_values=initial_values, **kwargs)

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    # TODO Copy this retry logic to all zwave devices
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30
    seconds.
    Args:
      **kwargs ():
    """

    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # TODO: self._sensitivity ??
    # sensitivity = 3 # index 4
    # timeout = 10 # index 8
    sensitivity = self._initial_values.get('_sensitivity', 3)
    timeout = self._initial_values.get('_timeout', 300)
    scale = 1  # index 64
    group1 = 241  # index 101
    interval = 300  # index 111

    self.node.set_config_param(4, sensitivity, 1)
    self.node.set_config_param(3, timeout)
    self.node.set_config_param(8, 8, 1)  # broadcast rate sec
    self.node.set_config_param(64, scale, size=1)  # THIS BROKE THINGS
    self.node.set_config_param(101, group1)
    self.node.set_config_param(111, interval)
    self.node.set_config_param(5, 1, 5)

    successful = True
    successful &= self.node.request_config_param(4) == sensitivity
    successful &= self.node.request_config_param(3) == timeout

    self._update_try_count += 1
    self._config_updated = successful

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    self._node = node

    super().update_from_zwave(node, **kwargs)

    if values is None:
      logging.message('ZWAVE MULTI SENSOR NO VALUES GIVEN')

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
    #Ultraviolet