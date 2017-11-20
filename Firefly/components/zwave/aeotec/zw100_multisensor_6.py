from Firefly import logging
from Firefly.components.zwave.device_types.multi_sensor import ZwaveMultiSensor
from Firefly.const import DEVICE_TYPE_MOTION, MOTION
from Firefly.helpers.device import *

COMMANDS = ['set_sensitivity']
DEVICE_TYPE = DEVICE_TYPE_MOTION
TITLE = 'Aeotec Gen6 MultiSensor'

ALARM = 'alarm'
BATTERY = 'battery'
DEVICE_TYPE_MULTI_SENSOR = 'multi_sensor'

REQUESTS = [MOTION, ALARM, LUX, TEMPERATURE, HUMIDITY, ULTRAVIOLET, BATTERY, 'sensitivity']

INITIAL_VALUES = {
  '_sensitivity': 2,
  '_timeout':     300.
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecMulti(firefly, package, **kwargs)
  firefly.install_component(sensor)
  logging.message('Finished Installing %s' % sensor.id)
  return sensor.id


class ZwaveAeotecMulti(ZwaveMultiSensor):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, **kwargs)

    self.add_request('sensitivity', self.get_sensitivity)
    self.add_command('set_sensitivity', self.set_sensitivity)
    # self.add_action('sensitivity',
    #                metaSlider(min=0, max=5, request_param='sensitivity', context='Set motion sensitivity (5 is most sensitive)', title='Motion sensitivity', set_command='set_sensitivity',
    #                           command_param='sensitivity'))

  def set_sensitivity(self, **kwargs):
    try:
      sensitivity = int(kwargs.get('sensitivity'))
      self._sensitivity = sensitivity
      if self._node:
        self.node.set_config_param(4, sensitivity, 1)
      self._update_try_count = 0
      self._config_updated = False
      self.update_device_config()
    except Exception as e:
      logging.error('AEOTEC MULTI 6 ERROR SETTING SENSITIVITY: %s' % str(e))

  def get_sensitivity(self, **kwargs):
    return self._sensitivity

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    # TODO Copy this retry logic to all zwave devices
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30
    seconds.
    Args:
      **kwargs ():
    """

    # Spec Sheet
    # https://aeotec.freshdesk.com/helpdesk/attachments/6028954764


    # sensitivity index 4
    sensitivity_idx = 4
    sensitivity_val = self._sensitivity
    sensitivity = (sensitivity_idx, sensitivity_val)

    # timeout = 10 # index 8
    timeout_idx = 3
    timeout_val = self._timeout
    timeout = (timeout_idx, timeout_val)

    # index 64 - This is the temp scale, 1 = F 0 = C
    scale_idx = 64
    scale_val = 1
    scale = (scale_idx, scale_val)

    # group1 is the data that should be broadcast with group1 241 = everything
    group1_idx = 101
    group1_val = 241  # index 101
    group1 = (group1_idx, group1_val)

    g1_interval_idx = 111
    g1_interval_val = 300  # index 111 - How often the group1 should be sent
    g1_interval = (g1_interval_idx, g1_interval_val)

    # Send binary sensor report when motion triggered.
    binary_sensor_idx = 5
    binary_sensor_val = 1
    binary_sensor = (binary_sensor_idx, binary_sensor_val, 1)

    # Limit event messages to only be threshold triggered
    threshold_enable_idx = 40
    enabled = 1
    disabled = 0
    threshold_enable = (threshold_enable_idx, enabled)

    # Set the threshold to trigger update for temperature (20 = 2.0 degree - default)
    temperature_threshold_idx = 41
    temperature_threshold_val = 5  # .5 degree
    temperature_threshold = (temperature_threshold_idx, temperature_threshold_val)

    # Set the threshold to trigger update humidity (10 = 10% - default)
    humidity_threshold_idx = 42
    humidity_threshold_val = 2
    humidity_threshold = (humidity_threshold_idx, humidity_threshold_val)

    # Set the threshold to trigger update luminance
    luminance_threshold_idx = 43
    luminance_threshold_val = 5
    luminance_threshold = (luminance_threshold_idx, luminance_threshold_val)

    successful_config = self.verify_set_zwave_params([
      binary_sensor,
      g1_interval,
      group1,
      humidity_threshold,
      luminance_threshold,
      scale,
      sensitivity,
      temperature_threshold,
      threshold_enable,
      timeout
    ])

    self._update_try_count += 1
    self._config_updated = successful_config
