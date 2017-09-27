from openzwave.network import ZWaveNode
from Firefly import scheduler
from uuid import uuid4

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, STATE
from Firefly.helpers.metadata import metaContact

from Firefly.util.zwave_command_class import COMMAND_CLASS_BATTERY, COMMAND_CLASS_SENSOR_BINARY, COMMAND_CLASS_ALARM

TITLE = 'Aeotec Zwave Window Door Sensor Gen5'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'alarm']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF,
  '_alarm': False
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecDoorWindow5(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecDoorWindow5(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._alarm = False
    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)
    self.add_request('alarm', self.get_alarm)

    self.add_action(CONTACT, metaContact(primary=True))

    self._alexa_export = False

    self.refreshed = False

    self.value_index = {
      'Burglar': -1,
      'Battery Level': -1,
      'Sensor': -1
    }

    if self.tags is []:
      self._tags = ['contact']

    self.refresh_id = str(uuid4())
    scheduler.runEveryM(5, self.refresh, self.refresh_id)

  def update_device_config(self, **kwargs):
    # TODO: Pull these out into config values
    """
    Updated the devices to the desired config params. This will be useful to make new default devices configs.

    For example when there is a gen6 multisensor I want it to always report every 5 minutes and timeout to be 30 
    seconds.
    Args:
      **kwargs ():
    """
    self.node.refresh_info()
    if self._update_try_count >= 5:
      self._config_updated = True
      return

    # TODO: self._sensitivity ??
    # https://github.com/OpenZWave/open-zwave/blob/master/config/aeotec/zw120.xml
    # self.node.set_config_param(2, 0)  # Disable 10 min wake up time
    self.node.set_config_param(121, 17)  # ensor Binary and Battery Report

    successful = True
    successful &= self.node.request_config_param(121) == 17

    self._update_try_count += 1
    self._config_updated = successful


  def initial_refresh(self, **kwargs):
    logging.error('ZWAVE DEBUG - INITIAL REFRESH')

    battery_values = self.node.get_values_for_command_class(COMMAND_CLASS_BATTERY)
    if len(battery_values) != 1:
      logging.error('ZWAVE DEBUG - more than one battery value reported')
    else:
      self.value_index['Battery Level'] = list(battery_values.keys())[0]

    sensor_values = self.node.get_values_for_command_class(COMMAND_CLASS_SENSOR_BINARY)
    if len(sensor_values) != 1:
      logging.error('ZWAVE DEBUG - more than one sensor value reported')
    else:
      self.value_index['Sensor'] = list(sensor_values.keys())[0]

    burglar_values = self.node.get_values_for_command_class(COMMAND_CLASS_ALARM)
    for z_id, z_obj in burglar_values.items():
      if z_obj.label != 'Burglar':
        continue
      self.value_index['Burglar'] = z_id
      break

    if self.value_index['Burglar'] != -1 and self.value_index['Battery Level'] != -1 and self.value_index['Sensor'] != -1:
      self.refreshed = True
      self.refresh()

  def refresh(self, **kwargs):
    if self.node is None:
      return

    logging.info('Refreshing ZWAVE')

    self.node.request_state()
    for prop, value_id in self.value_index.items():
      new_value = self.node.refresh_value(value_id)

      if prop == 'Sensor':
        self._state = CONTACT_OPEN if new_value else CONTACT_CLOSED
      if prop == 'Battery Level':
        self._battery = new_value
      if prop == 'Burglar':
        self._alarm = new_value == 3


  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    logging.message('ZWAVE DEBUG INITAL: %s' % str(node))
    logging.message('ZWAVE DEBUG INITAL INITAL: %s' % str(node))

    if node is None:
      return

    try:
      super().update_from_zwave(node, **kwargs)
    except Exception as e:
      logging.message('ZWAVE ERROR: %s' % str(e))

    logging.message('ZWAVE DEBUG SECOND: %s' % str(kwargs))


    if not self.refreshed:
      self.initial_refresh()

    if not self.refreshed:
      return

    logging.error('ZWAVE DEBUG - POST INITIAL REFRESH')

    logging.message('ZWAVE DEBUG: %s' % str(self.value_index))
    logging.message('ZWAVE DEBUG: %s' % str(node.values[self.value_index['Sensor']].data))

    self._state = CONTACT_OPEN if node.values[self.value_index['Sensor']].data else CONTACT_CLOSED
    self._alarm = True if node.values[self.value_index['Burglar']].data == 3 else False
    self._battery = node.values[self.value_index['Battery Level']].data


  def get_state(self, **kwargs):
    return self.state

  def get_alarm(self, **kwargs):
    return self._alarm

  @property
  def state(self):
    return self._state
