from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH, SWITCH)
from Firefly.helpers.metadata import metaSwitch

TITLE = 'Firefly Zwave Switch'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE]
REQUESTS = [STATE, SWITCH]
INITIAL_VALUES = {'_state': EVENT_ACTION_OFF}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = ZwaveSwitch(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class ZwaveSwitch(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    if self._node:
      self._switches = list(self._node.get_switches().keys())
    else:
      self._switches = None

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)

    self.add_request(STATE, self.get_state)
    self.add_request(SWITCH, self.get_state)

    self.add_action(STATE, metaSwitch(primary=True))

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return

    super().update_from_zwave(node, **kwargs)

    values = kwargs.get('values')
    if values is None:
      return
    genre = values.genre
    if genre != 'User':
      return

    if self._switches is None:
      self._switches = list(self._node.get_switches().keys())

    if node.get_switch_state(self._switches[0]):
      self._state = EVENT_ACTION_ON
    else:
      self._state = EVENT_ACTION_OFF

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

  @property
  def state(self):
    return self._state
