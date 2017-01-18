from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON,
                           ACTION_TOGGLE, DEVICE_TYPE_DIMMER, ACTION_LEVEL, LEVEL, EVENT_ACTION_LEVEL)
from Firefly.components.virtual_devices import AUTHOR
from Firefly.helpers.device import Device


TITLE = 'Firefly Virtual Dimmer'
DEVICE_TYPE = DEVICE_TYPE_DIMMER
AUTHOR = AUTHOR
COMMANDS = [ACTION_OFF, ACTION_ON, ACTION_TOGGLE, ACTION_LEVEL]
REQUESTS = [STATE, LEVEL]
INITIAL_VALUES = {'_state': STATE_OFF,
                  '_level': 100}

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
    self.add_command(ACTION_LEVEL, self.set_level)

    self.add_request(STATE, self.get_state)
    self.add_request(LEVEL, self.get_level)

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

  def set_level(self, **kwargs):
    level = int(kwargs.get('level'))
    event_actions = [EVENT_ACTION_LEVEL]
    if level is None:
      return False
    if level > 100:
      level = 100
    if level == 0 and self.state == STATE_ON:
      self.off()
      event_actions.append(EVENT_ACTION_OFF)
    if level > 0 and self.state == STATE_OFF:
      self.on()
      event_actions.append(EVENT_ACTION_ON)

    self._level = level
    return event_actions

  def get_state(self, **kwargs):
    return self.state

  def get_level(self, **kwargs):
    return self.level

  @property
  def state(self):
    return self._state

  @property
  def level(self):
    return self._level