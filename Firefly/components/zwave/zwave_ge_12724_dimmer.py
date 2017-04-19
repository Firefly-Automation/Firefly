from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH, DEVICE_TYPE_DIMMER, LEVEL)

TITLE = 'Firefly GE Dimmer'
DEVICE_TYPE = DEVICE_TYPE_DIMMER
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, LEVEL]
REQUESTS = [STATE, LEVEL]
INITIAL_VALUES = {'_state': EVENT_ACTION_OFF}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = GEDimmer(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class GEDimmer(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    if self._node:
      self._dimmers = list(self._node.get_dimmers().keys())
    else:
      self._dimmers = None
    self._level = 0

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)
    self.add_command(LEVEL, self.set_level)

    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

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

    if self._dimmers is None:
      self._dimmers = list(self._node.get_dimmers().keys())

    self._level = node.get_dimmer_level(self._dimmers[0])

    if self.level == 0:
      self._state = EVENT_ACTION_OFF
    else:
      self._state = EVENT_ACTION_OFF

    state_after = self.get_all_request_values()
    self.broadcast_changes(state_before, state_after)

  def set_level(self, **kwargs):
    level = 100
    try:
      level = int(kwargs.get('level', 100))
    except Exception as e:
      logging.error('[GE DIMMER] Error parsing level.')

    if self.node is None:
      logging.error('[GE Dimmer] Node is not set yet.')
      return
    self.node.set_dimmer(self._dimmers[0], level)
    self._level = level


  def off(self, **kwargs):
    self._state = EVENT_ACTION_OFF
    print(self._switches)
    self._node.set_switch(self._switches[0], 0)
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self._state = EVENT_ACTION_ON
    self._node.set_switch(self._switches[0], 1)
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == EVENT_ACTION_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def get_level(self, **kwargs):
    return self.level

  @property
  def level(self):
    return self._level

  @property
  def state(self):
    return self._state
