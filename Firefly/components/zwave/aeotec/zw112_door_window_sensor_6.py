from Firefly import logging
from Firefly.components.zwave.device_types.contact_sensor import ZwaveContactSensor
from Firefly.const import CONTACT, CONTACT_CLOSED

ALARM = 'alarm'
BATTERY = 'battery'

TITLE = 'ZW112 Aeotec Door/Window Sensor'

COMMANDS = []
REQUESTS = [ALARM, BATTERY, CONTACT]

INITIAL_VALUES = {
  '_alarm':   False,
  '_battery': -1,
  '_contact': CONTACT_CLOSED
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZW112(firefly, package, **kwargs)
  firefly.install_component(sensor)
  return sensor.id


class ZW112(ZwaveContactSensor):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    print(str(kwargs))
    super().__init__(firefly, package, TITLE, **kwargs)

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    Args:
      **kwargs ():
    """
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/zw112.xml

    if self.node is None:
      return
    if not self.node.is_ready:
      return
    if self._update_try_count >= 5:
      self._config_updated = True
      return

    self.node.set_config_param(121, 3)  # Sensor Binary and Battery Report

    successful = True
    successful &= self._config_params.get('Report Type to Send', -1) == 3

    self._update_try_count += 1
    self._config_updated = successful
