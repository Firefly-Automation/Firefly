from Firefly import logging
from Firefly.components.zwave.device_types.contact_sensor import ZwaveContactSensor
from Firefly.const import CONTACT, CONTACT_CLOSED

ALARM = 'alarm'
BATTERY = 'battery'

TITLE = 'DSB04100 Aeotec Door/Window Sensor'

COMMANDS = []
REQUESTS = [ALARM, BATTERY, CONTACT]

INITIAL_VALUES = {
  '_alarm':   False,
  '_battery': -1,
  '_contact': CONTACT_CLOSED
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZW120(firefly, package, **kwargs)
  firefly.install_component(sensor)
  return sensor.id


class ZW120(ZwaveContactSensor):
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

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30
    seconds.
    Args:
      **kwargs ():
    """
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/zw120.xml

    if self.node is None:
      return
    if not self.node.is_ready:
      return
    if self._update_try_count >= 5:
      self._config_updated = True
      return


    self.node.set_config_param(121, 17)  # Sensor Binary and Battery Report

    successful = True
    successful &= self._config_params['determines which report will be sent when magnet switch is opened/ closed'] == 17

    self._update_try_count += 1
    self._config_updated = successful
