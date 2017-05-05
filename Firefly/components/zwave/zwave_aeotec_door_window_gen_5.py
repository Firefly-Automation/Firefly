from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, STATE
from Firefly.helpers.metadata import metaContact

TITLE = 'Aeotec Zwave Window Door Sensor Gen5'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'alarm']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF
}


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

    self.add_action(STATE, metaContact(primary=True))

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30 
    seconds.
    Args:
      **kwargs ():
    """
    self.node.refresh_info()
    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # TODO: self._sensitivity ??
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/zw120.xml
    self.node.set_config_param(2, 0)  # Disable 10 min wake up time
    self.node.set_config_param(121, 17)  # ensor Binary and Battery Report

    successful = True
    successful &= self.node.request_config_param(2) == 0
    successful &= self.node.request_config_param(121) == 17

    self._update_try_count += 1
    self._config_updated = successful

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
