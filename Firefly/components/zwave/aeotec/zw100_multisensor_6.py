from Firefly import logging
from Firefly.components.zwave.device_types.multi_sensor import ZwaveMultiSensor
from Firefly.const import DEVICE_TYPE_MOTION, MOTION, LUX
from Firefly.helpers.metadata import metaSlider

TITLE = 'Aeotec Gen6 MultiSensor'
DEVICE_TYPE = DEVICE_TYPE_MOTION
AUTHOR = 'Zachary Priddy'
COMMANDS = ['set_sensitivity']

BATTERY = 'battery'
TEMPERATURE = 'temperature'
HUMIDITY = 'humidity'
ALARM = 'alarm'
DEVICE_TYPE_MULTI_SENSOR = 'multi_sensor'
ULTRAVIOLET = 'ultraviolet'

REQUESTS = [
  MOTION,
  ALARM,
  LUX,
  TEMPERATURE,
  HUMIDITY,
  ULTRAVIOLET,
  BATTERY,
  'sensitivity'
]

INITIAL_VALUES = {
  '_sensitivity': 3,
  '_timeout':     300.
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecMulti(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
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
    self.add_action('sensitivity',
                    metaSlider(min=0, max=5, request_param='sensitivity', context='Set motion sensitivity (5 is most sensitive)', title='Motion sensitivity', set_command='set_sensitivity',
                               command_param='sensitivity'))

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

    if self._node is None:
      return
    if not self._node.is_ready:
      logging.warn('ZWAVE NODE NOT READY FOR CONFIG')
      self._update_try_count = 0
      return

    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # Spec Sheet
    # https://aeotec.freshdesk.com/helpdesk/attachments/6028954764

    # TODO: self._sensitivity ??
    # sensitivity = 3 # index 4
    # timeout = 10 # index 8
    sensitivity = self._sensitivity
    timeout = self._initial_values.get('_timeout', 300)
    self.node.set_config_param(4, sensitivity, 1)
    self.node.set_config_param(3, timeout)

    scale = 1  # index 64 - This is the temp scale, 1 = F 0 = C
    self.node.set_config_param(64, scale, size=1)  # THIS BROKE THINGS

    # group1 is the data that should be broadcast with group1 241 = everything
    group1 = 241  # index 101
    self.node.set_config_param(101, group1)

    interval = 300  # index 111 - How often the group1 should be sent
    self.node.set_config_param(111, interval)

    # Send binary sensor report when motion triggered.
    self.node.set_config_param(5, 1, 1)

    successful = True
    successful &= self.node.request_config_param(4) == sensitivity
    successful &= self.node.request_config_param(3) == timeout

    self._update_try_count += 1
    self._config_updated = successful
