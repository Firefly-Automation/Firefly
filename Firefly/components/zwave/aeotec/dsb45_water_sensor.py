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
    initial_values = INITIAL_VALUES
    if kwargs.get('initial_values') is not None:
      initial_values_updated = INITIAL_VALUES.copy()
      initial_values_updated.update(kwargs.get('initial_values'))
      initial_values = initial_values_updated

    kwargs.update({
      'initial_values': initial_values,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, **kwargs)

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.


    Args:
      **kwargs ():
    """

    # Config Ref:
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/dsb45.xml
    wake_up_on_power_on_idx = 2
    wake_up_on_power_on = 1
    # self.node.set_config_param(wake_up_on_power_on_idx, wake_up_on_power_on)

    report_to_send_idx = 121
    report_to_send_val = 4113  # OZW Ideal Setting: 0x1011 (Battery, Sensor Binary Report, Alarm)
    report_to_send = (report_to_send_idx, report_to_send_val)

    successful = self.verify_set_zwave_params([report_to_send])

    self._update_try_count += 1
    self._config_updated = successful
