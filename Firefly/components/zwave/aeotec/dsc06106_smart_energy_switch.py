from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import ACTION_OFF, ACTION_ON, SWITCH

TITLE = 'Aeotec Smart Switch 5'

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
  sensor = ZwaveAeotecSwitch5(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecSwitch5(ZwaveSwitch):
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

    # REF:
    # https://aeotec.freshdesk.com/helpdesk/attachments/6009584529
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/dsc06106.xml

    # Configure what kind of reports to send and when to send them.
    self.node.set_config_param(101, 4)
    self.node.set_config_param(102, 4)
    self.node.set_config_param(111, 30)

    # What kind of report to send
    report_idx = 80
    report_node = 0
    report_hail = 1
    report_basic = 2
    report_type = report_basic
    self.node.set_config_param(report_idx, report_basic)

    # The three options below keep the device from reporting every 10 seconds. Mainly param 90 that enables only send report when triggered.

    # Min change in watts to trigger report (see below) [default 50]
    min_change_watts_idx = 91
    min_change_watts = 50
    self.node.set_config_param(min_change_watts_idx, min_change_watts)

    # Min change in watts % to trigger report (see below) [default 10]
    min_change_watts_pct_idx = 92
    min_change_watts_pct = 10
    self.node.set_config_param(min_change_watts_pct_idx, min_change_watts_pct)

    # Send wattage reports only when wattage changes by default 10%
    report_on_wattage_change = 90
    self.node.set_config_param(report_on_wattage_change, 1, 1)


    # TODO: Fix this logic to actually get the current values by index. This means we will have to index value by param ID not label.
    successful = True
    successful &= self.node.request_config_param(report_idx) == report_type
    successful &= self.node.request_config_param(102) == 15


    self._update_try_count += 1
    self._config_updated = successful
