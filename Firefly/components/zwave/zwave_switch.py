from Firefly import logging
from Firefly.helpers.device import Device


from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH)




TITLE = 'Firefly Zwave Switch'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE]
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': STATE_OFF}

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = ZwaveSwitch(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch
  return new_switch.id


class ZwaveSwitch(Device):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._node = kwargs.get('node')
    self._switches = list(self._node.get_switches().keys())

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)

    self.add_request(STATE, self.get_state)

  def off(self, **kwargs):
    self._state = STATE_OFF
    print(self._switches)
    self._node.set_switch(self._switches[0], 0)
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self._state = STATE_ON
    self._node.set_switch(self._switches[0], 1)
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == STATE_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  def update_from_zwave(self, node, **kwargs):
    if node.get_switch_state(self._switches[0]):
      self._state = STATE_ON
    else:
      self._state = STATE_OFF

  @property
  def state(self):
    return self._state
