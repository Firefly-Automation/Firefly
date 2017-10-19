from Firefly import logging
from Firefly.components.zwave.device_types.contact_sensor import ZwaveContactSensor
from openzwave.network import ZWaveNode
from openzwave.value import ZWaveValue


TITLE = 'Ecolink Contact Sensor'


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ContactSensor(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ContactSensor(ZwaveContactSensor):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, values: ZWaveValue = None, values_only=False, **kwargs):
    if node is None:
      return

    if not node.values[self.value_map['Sensor']].is_polled:
      node.values[self.value_map['Sensor']].enable_poll()

    super().update_from_zwave(node, ignore_update, values, values_only, **kwargs)


