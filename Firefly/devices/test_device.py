from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON)

from Firefly.helpers.device import Device


TITLE = 'Test Light Device'
AUTHOR = 'Zachary Priddy - me@zpriddy.com'
# Writing install package to device instead of metadata package so reinstall scripts will function correctly.
PACKAGE = 'TestDevice'
COMMANDS = [ACTION_OFF, ACTION_ON]
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': STATE_OFF}


def Setup(firefly, install_package, device_id='', alias='', **kwargs):
  logging.info('Entering Device Setup')
  new_device = TestDevice(firefly, install_package, device_id=device_id, alias=alias, **kwargs)
  firefly._devices[new_device.id] = new_device

class TestDevice(Device):
  def __init__(self, firefly, install_package, device_id='', alias='', **kwargs):
    super().__init__(firefly, device_id, TITLE, AUTHOR, install_package, COMMANDS, REQUESTS, INITIAL_VALUES, alias=alias)

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)

    self.add_request(STATE, self.get_state)

    initial_values = INITIAL_VALUES if not kwargs.get('initial_values') else kwargs.get('initial_values')

    # TODO: Is this really the best way to do this?
    self.__dict__.update(initial_values)


  def off(self, **kwargs):
    self._state = STATE_OFF
    return EVENT_ACTION_OFF

  def on(self, **kwargs):
    self._state = STATE_ON
    return EVENT_ACTION_ON

  def get_state(self, **kwargs):
    return self.state

  @property
  def state(self):
    return self._state