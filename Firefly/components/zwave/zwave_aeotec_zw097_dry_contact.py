from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, DEVICE_TYPE_SWITCH, STATE
from Firefly.helpers.metadta.metadata import metaWaterLevel

TITLE = 'Aeotec Zwave ZW097 Dry Conact'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT]
INITIAL_VALUES = {
  '_state': CONTACT_CLOSED
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecDryContact(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecDryContact(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)

    self._alarm = False

    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)

    self.add_action(CONTACT, metaWaterLevel())

    self._alexa_export = False

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30 
    seconds.
    Args:
      **kwargs ():
    """
    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/zw097.xml
    #self.node.set_config_param(2, 0, size=1)  # Disable 10 min wakeup
    #self.node.set_config_param(121, 272, size=4)

    successful = True
    #successful &= self.node.request_config_param(2) == 0

    self._update_try_count += 1
    self._config_updated = successful

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return
    print(kwargs)

    print('water 1')
    values = kwargs.get('values')
    if values is None:
      return

    print(values)

    print(values.data)

    self._state = CONTACT_OPEN if values.data == 255 else CONTACT_CLOSED

    try:
      super().update_from_zwave(node, **kwargs)
    except Exception as e:
      print(e)


    #genre = values.genre
    #if genre != 'User':
    #  return

    print('water 2')
    #self._state = CONTACT_OPEN if values.data == 255 else CONTACT_CLOSED
    #self._state = CONTACT_OPEN if self.get_sensors(sensor='sensor') is True else CONTACT_CLOSED

  def get_state(self, **kwargs):
    return self.state

  @property
  def state(self):
    return self._state
