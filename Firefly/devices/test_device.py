from Firefly import logging
from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE, EVENT_ACTION_OFF, EVENT_ACTION_ON)

from Firefly.helpers.device import Device


TITLE = 'Test Light Device'
AUTHOR = 'Zachary Priddy - me@zpriddy.com'
PACKAGE = 'TestDevice'
COMMANDS = [ACTION_OFF, ACTION_ON]
REQUESTS = [STATE]
INITIAL_VALUES = {'_state': STATE_OFF}


def Setup(firefly, device_id='', alias=''):
  logging.info('Entering Device Setup')
  new_device = TestDevice(firefly, device_id=device_id, alias=alias)
  firefly._devices[new_device.id] = new_device
  return {'title': TITLE, 'author': AUTHOR, 'package': PACKAGE, 'commands': COMMANDS, 'requests': REQUESTS}

class TestDevice(Device):
  def __init__(self, firefly, device_id='', alias=''):
    super().__init__(firefly, device_id, TITLE, AUTHOR, PACKAGE, COMMANDS, REQUESTS, alias=alias)

    self.add_command(ACTION_OFF, self.off)
    self.add_command(ACTION_ON, self.on)

    self.add_request(STATE, self.get_state)

    # TODO: Is this really the best way to do this?
    self.__dict__.update(INITIAL_VALUES)


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