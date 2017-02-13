from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.helpers.device import Device
from Firefly.util.get_from_kwargs import get_kwargs_value
from Firefly.helpers.events import Event
import asyncio
from openzwave.network import ZWaveNode
from Firefly import logging
from Firefly.const import (STATE, SENSORS, DEVICE_TYPE_MOTION, EVENT_TYPE_BROADCAST)



TITLE = 'Aeotec Gen6 MultiSensor'
DEVICE_TYPE = DEVICE_TYPE_MOTION
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': False, '_sensitivity': 4}

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecMulti(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecMulti(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_request(STATE, self.get_state)


  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30 seconds.
    Args:
      **kwargs ():
    """
    # TODO: self._sensitivity ??
    sensitivity = 4 # index 4
    timeout = 30 # index 8
    scale = 2 # index 64
    group1 = 241 # index 101
    interval = 300 #index 111

    self.node.set_config_param(4, sensitivity)
    self.node.set_config_param(8, timeout)
    self.node.set_config_param(64, scale)
    self.node.set_config_param(101, group1)
    self.node.set_config_param(111, interval)

    self._config_updated = True

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
