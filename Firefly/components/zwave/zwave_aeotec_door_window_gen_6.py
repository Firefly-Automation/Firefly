from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.components.zwave.zwave_device import ZwaveDevice
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, DEVICE_TYPE_SWITCH, EVENT_ACTION_OFF, STATE
from Firefly.helpers.metadata import metaContact

TITLE = 'Aeotec Zwave Window Door Sensor Gen6'
DEVICE_TYPE = DEVICE_TYPE_SWITCH
AUTHOR = 'Zachary Priddy'
COMMANDS = []
REQUESTS = [STATE, CONTACT, 'alarm']
INITIAL_VALUES = {
  '_state': EVENT_ACTION_OFF
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup' % TITLE)
  sensor = ZwaveAeotecDoorWindow6(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[sensor.id] = sensor
  return sensor.id


class ZwaveAeotecDoorWindow6(ZwaveDevice):
  def __init__(self, firefly, package, **kwargs):
    if kwargs.get('initial_values') is not None:
      INITIAL_VALUES.update(kwargs['initial_values'])
    kwargs['initial_values'] = INITIAL_VALUES
    super().__init__(firefly, package, TITLE, AUTHOR, COMMANDS, REQUESTS, DEVICE_TYPE, **kwargs)
    self.__dict__.update(kwargs['initial_values'])

    self._state = CONTACT_CLOSED
    self._alarm = False

    self.add_request(STATE, self.get_state)
    self.add_request(CONTACT, self.get_state)
    self.add_request('alarm', self.get_alarm)

    self.add_action(CONTACT, metaContact(primary=True))

    self._alexa_export = False

    if self.tags is []:
      self._tags = ['contact']

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
    self.node.set_config_param(121, 2, 1)  # Sensor Binary and Battery Report

    successful = True
    successful &= self.node.request_config_param(121) == 3

    self._update_try_count += 1
    self._config_updated = successful

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    if node is None:
      return

    super().update_from_zwave(node, **kwargs)

    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    #print(kwargs.__dict__)
    sensors = node.get_sensors()
    print(sensors)
    try:
      print(list(sensors))
    except:
      pass
    try:
      print(type(sensors))
    except:
      pass
    #print(node.get_sensors().keys()[0])
    #print(node.get_sensor_value())
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&+++')



    values = kwargs.get('values')
    if values is None:
      return

    genre = values.genre
    if genre != 'User':
      return

    b = self._raw_values.get('burglar')
    print(b)
    if b:
      self._alarm = b.get('value') == 3
    else:
      self._alarm = False

    sensor = self._raw_values.get('sensor')
    contact_state = False
    if sensor:
      contact_state = sensor.get('value')

    # TODO: Move this to zwave device
    battery = self._raw_values.get('battery level')
    print('+++++++++++++++++++++++++++++++++++++++')
    print(str(battery))
    print('+++++++++++++++++++++++++++++++++++++++')
    if battery:
      self._battery = battery.get('value')

    self._state = CONTACT_OPEN if contact_state is True else CONTACT_CLOSED

  def get_state(self, **kwargs):
    return self.state

  def get_alarm(self, **kwargs):
    return self._alarm

  @property
  def state(self):
    return self._state
