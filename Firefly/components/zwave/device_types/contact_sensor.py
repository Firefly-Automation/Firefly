from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import AUTHOR, CONTACT, DEVICE_TYPE_CONTACT
from Firefly.helpers.device_types.contact_sensor import ContactSensor

ALARM = 'alarm'
BATTERY = 'battery'

CAPABILITIES = {
  ALARM:   True,
  BATTERY: True,
  CONTACT: True,
}

COMMANDS = []

REQUESTS = [ALARM, BATTERY, CONTACT]


class ZwaveContactSensor(ContactSensor, ZwaveDevice):
  def __init__(self, firefly, package, title='Zwave Contact Sensor', initial_values={}, value_map={}, **kwargs):
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

    super().__init__(firefly, package, title, AUTHOR, commands, requests, DEVICE_TYPE_CONTACT, capabilities=CAPABILITIES, initial_values=initial_values, **kwargs)

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

    logging.info('NODE LAST UPDATE: %s' % str(node.last_update))

    if values is None:
      logging.message('ZWAVE CONTACT SENSOR NO VALUES GIVEN')
      super().update_from_zwave(node, **kwargs)
      if node.is_ready:
        for label, value_id in self.value_map.items():
          logging.info('REFRESHING VALUE %s' % label)
          self.node.refresh_value(value_id)
      return

    #if node.is_ready and node.is_awake and not self.refreshed:
    #  for label, value_id in self.value_map.items():
    #    logging.info('REFRESHING VALUE %s' % label)
    #    self.node.refresh_value(value_id)
    #  self.refreshed = True

    label = values.label
    logging.info('[ZWAVE] Value label: %s data: %s' % (label, values.data))
    if label in ['Sensor', 'Battery Level', 'Burglar']:
      self.value_map[label] = values.value_id
      if label == 'Sensor':
        self.update_values(contact=values.data)
      if label == 'Battery Level':
        self.update_values(battery=values.data)
      if label == 'Burglar':
        self.update_values(alarm=values.data)

    elif label == 'Basic':
      self.update_values(contact=(values.data==255))

    super().update_from_zwave(node, **kwargs)
