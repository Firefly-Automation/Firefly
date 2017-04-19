from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (STATE, EVENT_ACTION_OFF, DEVICE_TYPE_SWITCH, CONTACT, CONTACT_CLOSED, CONTACT_OPEN)

TITLE = 'Zwave Generic Window Door Sensor'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'alarm']
INITIAL_VALUES = {'_state': EVENT_ACTION_OFF}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecDoorWindow5(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecDoorWindow5(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._state = CONTACT_CLOSED
    self._alarm = False

    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)
    self.add_request('alarm', self.get_alarm)


  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return

    state_before = self.get_all_request_values()
    super().update_from_zwave(node, **kwargs, ignore_update=True)

    values = kwargs.get('values')
    if values is None:
      state_after = self.get_all_request_values()
      self.broadcast_changes(state_before, state_after)
      return
    genre = values.genre
    if genre != 'User':
      state_after = self.get_all_request_values()
      self.broadcast_changes(state_before, state_after)
      return

    b = self._raw_values.get('burglar')
    print(b)
    if b:
      self._alarm = b.get('value') == 3
    else:
      self._alarm = False

    self._state = CONTACT_OPEN if self.get_sensors(sensor='sensor') is True else CONTACT_CLOSED

    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

  def get_state(self, **kwargs):
    return self.state

  def get_alarm(self, **kwargs):
    return self._alarm

  @property
  def state(self):
    return self._state
