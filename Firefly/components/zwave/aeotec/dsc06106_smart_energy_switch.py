from Firefly import logging
from Firefly.components.zwave.device_types.switch import ZwaveSwitch
from Firefly.const import ACTION_OFF, ACTION_ON, SWITCH
from Firefly.services.alexa.alexa_const import ALEXA_SMARTPLUG

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
  switch = ZwaveAeotecSwitch5(firefly, package, **kwargs)
  return firefly.install_component(switch)

class ZwaveAeotecSwitch5(ZwaveSwitch):
  def __init__(self, firefly, package, **kwargs):
    initial_values = INITIAL_VALUES
    if kwargs.get('initial_values') is not None:
      initial_values_updated = INITIAL_VALUES.copy()
      initial_values_updated.update( kwargs.get('initial_values'))
      initial_values = initial_values_updated

    kwargs.update({
      'initial_values': initial_values,
      'commands':       COMMANDS,
      'requests':       REQUESTS
    })
    super().__init__(firefly, package, TITLE, capabilities=CAPABILITIES, alexa_categories=[ALEXA_SMARTPLUG], **kwargs)

    self.set_alexa_categories(['SMARTPLUG'])
    self._alexa_categories = ['SMARTPLUG']

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    # TODO Copy this retry logic to all zwave devices
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    Args:
      **kwargs ():
    """

    # REF:
    # https://aeotec.freshdesk.com/helpdesk/attachments/6009584529
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/dsc06106.xml

    # Configure what kind of reports to send and when to send them.
    # TODO: Document these
    r1 = (101, 4)
    r2 = (102, 4)
    r3 = (111, 30)

    # What kind of report to send
    report_idx = 80
    report_node = 0
    report_hail = 1
    report_basic = 2
    report_type = report_basic
    report = (report_idx, report_basic)

    # The three options below keep the device from reporting every 10 seconds. Mainly param 90 that enables only send report when triggered.

    # Min change in watts to trigger report (see below) [default 50]
    min_change_watts_idx = 91
    min_change_watts_val = 50
    min_change_watts = (min_change_watts_idx, min_change_watts_val)

    # Min change in watts % to trigger report (see below) [default 10]
    min_change_watts_pct_idx = 92
    min_change_watts_pct_val = 10
    min_change_watts_pct = (min_change_watts_pct_idx, min_change_watts_pct_val)

    # Send wattage reports only when wattage changes by default 10%
    report_on_wattage_change_idx = 90
    report_on_wattage_change = (report_on_wattage_change_idx, 1, 1)

    successful = self.verify_set_zwave_params([
      min_change_watts,
      min_change_watts_pct,
      r1,
      r2,
      r3,
      report,
      report_on_wattage_change
    ])

    self._update_try_count += 1
    self._config_updated = successful
