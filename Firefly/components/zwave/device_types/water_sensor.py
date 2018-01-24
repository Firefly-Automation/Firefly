from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import AUTHOR, DEVICE_TYPE_MOTION, WATER
from Firefly.helpers.device_types.water_sensor import WaterSensor

ALARM = 'alarm'
BATTERY = 'battery'

CAPABILITIES = {
  ALARM:   True,
  BATTERY: True,
  WATER:   True,
}

COMMANDS = []

REQUESTS = [ALARM, BATTERY, WATER]


class ZwaveWaterSensor(WaterSensor, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Water Sensor', initial_values={}, value_map={}, **kwargs):
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

    self.value_map = value_map
    self.refreshed = False

  def export(self, current_values: bool = True, api_view: bool = False, **kwargs):
    export_data = super().export(current_values, api_view)
    export_data['value_map'] = self.value_map
    return export_data

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    self._node = node

    super().update_from_zwave(node, **kwargs)

    logging.info('NODE LAST UPDATE: %s' % str(node.last_update))

    if values is None:
      logging.message('ZWAVE WATER SENSOR NO VALUES GIVEN')
      if node.is_ready:
        for label, value_id in self.value_map.items():
          logging.info('REFRESHING VALUE %s' % label)
          self.node.refresh_value(value_id)
      return

    if node.is_ready and node.is_awake and not self.refreshed:
      for label, value_id in self.value_map.items():
        logging.info('REFRESHING VALUE %s' % label)
        self.node.refresh_value(value_id)
      self.refreshed = True

    label = values.label

    if label == 'Sensor':
      self.update_values(water=values.data)
      self.value_map[values.label] = values.value_id
    if label == 'Battery Level':
      self.update_values(battery=values.data)
      self.value_map[values.label] = values.value_id
    if label == 'Flood':
      self.update_values(alarm=values.data)
      self.value_map[values.label] = values.value_id
