from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (STATE, DEVICE_TYPE_MOTION, MOTION, MOTION_ACTIVE, MOTION_INACTIVE)

TITLE = 'Firefly Zwave Motion Sensor'
DEVICE_TYPE = DEVICE_TYPE_MOTION
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': False}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveMotionSensor(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveMotionSensor(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_request(STATE, self.get_state)
    self.add_request(MOTION, self.get_motion)

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    state_before = self.get_all_request_values()
    super().update_from_zwave(node, **kwargs, ignore_update=True)

    # self._state = get_kwargs_value(self._sensors, 'SENSOR', False)
    b = self._raw_values.get('burglar')
    print(b)
    if b:
      self._state = b.get('value') == 8
    else:
      self._state = False

    # self._state = self._raw_values.get('BURGLAR')

    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

  def get_state(self, **kwargs):
    return self.state

  def get_motion(self, **kwargs):
    return MOTION_ACTIVE if self.state else MOTION_INACTIVE

  @property
  def state(self):
    self._state = self._sensors.get('sensor')
    return self._state
