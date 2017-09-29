from Firefly import logging
from Firefly.components.zwave.device_types.contact_sensor import ZwaveContactSensor

TITLE = 'Zwave Contact Sensor'


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ContactSensor(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ContactSensor(ZwaveContactSensor):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)
