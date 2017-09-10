from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import (STATE, EVENT_ACTION_OFF, DEVICE_TYPE_SWITCH, CONTACT, CONTACT_CLOSED, CONTACT_OPEN)
from Firefly.helpers.metadata import metaContact

TITLE = 'Ecolink Door/Window+'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'alarm']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = EcolinkDoorWindosPlus(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class EcolinkDoorWindosPlus(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    if kwargs.get('tags') is None:
      kwargs['tags'] = ['contact']
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._state = CONTACT_CLOSED
    self._alarm = False

    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)
    self.add_request('alarm', self.get_alarm)

    self.add_action(CONTACT, metaContact(primary=True))

    self._alexa_export = False

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

    b = self._raw_values.get('burglar')
    print(b)
    if b:
      self._alarm = b.get('value') == 3
    else:
      self._alarm = False

    self._state = CONTACT_OPEN if self.get_sensors(sensor='sensor') is True else CONTACT_CLOSED

  def get_state(self, **kwargs):
    return self.state

  def get_alarm(self, **kwargs):
    return self._alarm

  @property
  def state(self):
    return self._state
