from Firefly import logging
from Firefly.components.zwave.device_types.motion_sensor import ZwaveMotionSensor
from Firefly.const import DEVICE_TYPE_MOTION

TITLE = 'Zwave Motion Sensor'
DEVICE_TYPE = DEVICE_TYPE_MOTION


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = MotionSensor(firefly, package, **kwargs)
  firefly.install_component(sensor)
  return sensor.id


class MotionSensor(ZwaveMotionSensor):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, **kwargs)
