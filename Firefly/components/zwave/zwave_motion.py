from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.helpers.device import Device
from Firefly.util.get_from_kwargs import get_kwargs_value
from Firefly.helpers.events import Event
import asyncio
from openzwave.network import ZWaveNode
from Firefly import logging
from Firefly.const import (EVENT_ACTION_OFF, EVENT_ACTION_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH, SENSORS, DEVICE_TYPE_MOTION, EVENT_TYPE_BROADCAST)



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

  #@asyncio.coroutine
  def update_from_zwave(self, node: ZWaveNode, **kwargs):
    sensor_before = self.state
    super().update_from_zwave(node, **kwargs)

    #self._state = get_kwargs_value(self._sensors, 'SENSOR', False)
    b = self._raw_values.get('BURGLAR')
    print(b)
    if b:
      self._state = b.get('value') == 8
    else:
      self._state = False

    #self._state = self._raw_values.get('BURGLAR')

    if self.state != sensor_before:
      broadcast = Event(self.id, EVENT_TYPE_BROADCAST, event_action='UPDATE')
      s = self._firefly.send_event(broadcast)
      logging.info(s)
      logging.info(broadcast)



  def get_state(self, **kwargs):
    return self.state

  @property
  def state(self):
    #self._state =  self._sensors.get('SENSOR')
    return self._state
