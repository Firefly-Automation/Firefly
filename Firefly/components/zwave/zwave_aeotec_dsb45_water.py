from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, STATE
from Firefly.helpers.metadata import metaWaterSensor

TITLE = 'Aeotec Zwave DSB45 Water Sensor'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'water']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_water': False
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
    self.__dict__.update(kwargs['initial_values'])
    
    self._alarm = False

    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)
    # TODO - Make this a const
    self.add_request('water', self.get_water)

    self.add_action(CONTACT, metaWaterSensor())

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
    self.node.set_config_param(121, 4113)

    successful = True
    successful &= self.node.request_config_param(121) == 4113

    self._update_try_count += 1
    self._config_updated = successful

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return

    super().update_from_zwave(node, **kwargs)

    values = kwargs.get('values')
    if values is None:
      return

    self._water = self.get_sensors(sensor='sensor') if self.get_sensors(sensor='sensor') else False
    self._state = CONTACT_OPEN if self._water is True else CONTACT_CLOSED

  def get_state(self, **kwargs):
    return self.state

  def get_water(self, **kwargs):
    return self._water

  @property
  def state(self):
    return self._state
