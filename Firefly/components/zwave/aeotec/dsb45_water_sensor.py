from Firefly import logging
from Firefly.components.zwave.device_types.water_sensor import ZwaveWaterSensor
from Firefly.const import SENSOR_DRY, WATER

ALARM = 'alarm'
BATTERY = 'battery'

TITLE = 'DSB45 Aeotec Water Sensor'

COMMANDS = []
REQUESTS = [ALARM, BATTERY, WATER]

INITIAL_VALUES = {
  '_alarm':   False,
  '_battery': -1,
  '_water':   SENSOR_DRY
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = DSB45(firefly, package, **kwargs)
  firefly.install_component(sensor)
  return sensor.id


class DSB45(ZwaveWaterSensor):
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

    if self._node is None:
      return
    if not self._node.is_ready:
      logging.warn('ZWAVE NODE NOT READY FOR CONFIG')
      self._update_try_count = 0
      # Removing this as this device does not seem to ever report 'ready'
      #return

    if self._update_try_count >= 5:
      self._config_updated = True
      return


    # Config Ref:
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/dsb45.xml
    wake_up_on_power_on_idx = 2
    wake_up_on_power_on = 1
    #self.node.set_config_param(wake_up_on_power_on_idx, wake_up_on_power_on)

    report_to_send_idx = 121
    report_to_send = 4113  # OZW Ideal Setting: 0x1011 (Battery, Sensor Binary Report, Alarm)
    self.node.set_config_param(report_to_send_idx, report_to_send)

    # TODO: Make config params index by id
    successful = True
    successful &= self.zwave_values[121]['value'] == report_to_send
    #successful &= self._config_params.get('wake up on power on') == wake_up_on_power_on

    self._update_try_count += 1
    self._config_updated = successful
