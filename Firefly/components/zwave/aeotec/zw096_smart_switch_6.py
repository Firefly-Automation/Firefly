from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import DEVICE_TYPE_MOTION, LUX, MOTION, ACTION_OFF, ACTION_ON, ALEXA_OFF, ALEXA_ON, ALEXA_SET_PERCENTAGE, DEVICE_TYPE_SWITCH, LEVEL, SWITCH
from Firefly.helpers.metadata import metaSlider


TITLE = 'Aeotec Smart Switch 6'

BATTERY = 'battery'
ALARM = 'alarm'
POWER_METER = 'power_meter'
VOLTAGE_METER = 'voltage_meter'

CURRENT = 'power_current'
CURRENT_ENERGY_READING = 'current_energy_reading'
PREVIOUS_ENERGY_READING = 'previous_energy_reading'
VOLTAGE = 'voltage'
WATTS = 'watts'

COMMANDS = [ACTION_OFF, ACTION_ON]
REQUESTS = [SWITCH, CURRENT, VOLTAGE, WATTS]

INITIAL_VALUES = {}

CAPABILITIES = {
  POWER_METER: True,
  SWITCH:      True,
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecSwitch6(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecSwitch6(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs.update({
      'initial_values': INITIAL_VALUES,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, capabilities=CAPABILITIES, **kwargs)


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
    # TODO: Find spec sheet

    # TODO: Document These
    report = 2  # 1=hail 2=basic
    self.node.set_config_param(110, 1)
    self.node.set_config_param(100, 1)
    self.node.set_config_param(80, report)
    self.node.set_config_param(102, 15)
    self.node.set_config_param(111, 30)

    successful = True
    successful &= self.node.request_config_param(80) == report
    successful &= self.node.request_config_param(102) == 15

    self._update_try_count += 1
    self._config_updated = successful



