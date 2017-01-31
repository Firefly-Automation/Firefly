from Firefly import logging
from Firefly.util.get_from_kwargs import get_kwargs_value

from Firefly.helpers.device import Device
from Firefly.helpers.events import Event
from openzwave.network import ZWaveNode

from Firefly.const import SENSORS, EVENT_TYPE_BROADCAST

class ZwaveDevice(Device):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):

    commands.append('ZWAVE_CONFIG')

    requests.append('SENSORS')
    requests.append('PARAMS')
    requests.append('RAW_VALUES')

    super().__init__(firefly, package, title, author, commands, requests, device_type, **kwargs)

    self._node = get_kwargs_value(kwargs, 'node')

    self._sensors = {}
    self._switches = {}
    self._config_params = {}
    self._raw_values = {}


    self.add_command('ZWAVE_CONFIG', self.zwave_config)

    self.add_request('SENSORS', self.get_sensors)
    self.add_request('PARAMS', self.get_params)
    self.add_request('RAW_VALUES', self.get_raw_values)


  def zwave_config(self, **kwargs):
    if self._node is None:
      logging.critical('FAILING TO UPDATE DEVICE')
      return False
    param = get_kwargs_value(kwargs, 'id')
    value = get_kwargs_value(kwargs, 'value')
    size = get_kwargs_value(kwargs, 'size', 2)

    if size:
      size = int(size)

    if param and value:
      param = int(param)
      value = int(value)
      self._node.set_config_param(param, value, size=size)

    self._node.refresh_info()
    self._node.request_state()

    return True


  def get_sensors(self, **kwargs):
    sensor = get_kwargs_value(kwargs, 'SENSOR')
    if sensor:
      s = self._sensors.get(sensor)
      return s
    return self._sensors


  def get_params(self, **kwargs):
    values = get_kwargs_value(kwargs, 'VALUE')
    if values:
      s = self._config_params.get(values)
      return s
    return self._config_params


  def get_raw_values(self, **kwargs):
    values = get_kwargs_value(kwargs, 'VALUE')
    if values:
      s = self._raw_values.get(values)
      return s
    return self._raw_values

  def update_from_zwave(self, node: ZWaveNode, **kwargs):
    '''
    Currently the update command is not in the COMMANDS -> THis is because it acts differently right now.. This may change in the near future.
    Args:
      node ():

    Returns:

    '''
    print('*******************************************')
    print(node)
    if node is None:
      return

    # This will set the node on the first update once zwave boots
    self._node = node

    # When security data changes sometimes you need to send a request to update the sensor value
    old_security_data = [b for a, b in self._raw_values.items() if b.get('class') == 113]

    for s, i in node.get_sensors().items():
      self._sensors[i.label.upper()] = i.data

    for s, i in node.get_values().items():
      if i.command_class == 112:
        self._config_params[i.label.upper()] = {'value': i.data, 'id': i.index}

      self._raw_values[i.label.upper()] = {'value': i.data, 'id': i.index, 'class': i.command_class}


    new_security_data = [b for a, b in self._raw_values.items() if b.get('class') == 113]

    # If any of the security values change issue update command
    #if old_security_data != new_security_data:
    #  self._node.refresh_info()
    #  self._node.request_state()

    # TODO: Figure out how to send the broadcast event, have to find what types of values changed.
    #broadcast = Event(self.id, EVENT_TYPE_BROADCAST, event_action='UPDATE')
    #self._firefly.send_event(broadcast)
    #logging.info(broadcast)
    #return True