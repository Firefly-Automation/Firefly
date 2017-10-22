from Firefly import logging
from Firefly.components.zwave.device_types.contact_sensor import ZwaveContactSensor

TITLE = 'Zwave Contact Sensor'


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ContactSensor(firefly, package, **kwargs)
  firefly.install_component(sensor)
  return sensor.id


class ContactSensor(ZwaveContactSensor):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)
