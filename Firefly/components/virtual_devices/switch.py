from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_SWITCH)
from Firefly.components.virtual_devices import AUTHOR
from Firefly.helpers.device import Device

from Firefly.helpers.metadata import metaSwitch


TITLE = 'Firefly Virtual Switch'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE]
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': STATE_OFF}

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  new_switch = VirtualSwitch(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[new_switch.id] = new_switch

class VirtualSwitch(Device):
  def __init__(self, firefly, package, **kwargs):
    kwargs['initial_values'] = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)
    self.add_command(ACTION_TOGGLE, self.toggle)

    self.add_request(STATE, self.get_state)

    self.add_action(STATE, metaSwitch())

    # TODO: Make HOMEKIT CONST
    self.add_homekit_export('HOMEKIT_SWITCH', STATE)


  def off(self, **kwargs):
    self._state = STATE_OFF
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self._state = STATE_ON
    return EVENT_ACTION_ON

  def toggle(self, **kwargs):
    if self.state == STATE_ON:
      return self.off()
    return self.on()

  def get_state(self, **kwargs):
    return self.state

  @property
  def state(self):
    return self._state