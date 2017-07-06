from openzwave.network import ZWaveNode

from Firefly import logging
from Firefly.helpers.device import Device


class ZwaveDevice(Device):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):

    commands.append('ZWAVE_CONFIG')
    commands.append('ZWAVE_UPDATE')

    requests.append('SENSORS')
    requests.append('PARAMS')
    requests.append('RAW_VALUES')
    requests.append('battery')

    super().__init__(firefly, package, title, author, commands, requests, device_type, **kwargs)

    self._node: ZWaveNode = kwargs.get('node')

    self._sensors = {}
    self._switches = {}
    self._config_params = {}
    self._raw_values = {}
    self._config_updated = False
    self._update_try_count = 0
    self._node_id = kwargs.get('node_id')

    self._manufacturer_id = ''
    self._manufacturer_name = ''
    self._product_name = ''
    self._product_type = ''

    self._battery = kwargs.get('battery', 'NOT REPORTED')

    self.add_command('ZWAVE_CONFIG', self.zwave_config)
    self.add_command('ZWAVE_UPDATE', self.update_from_zwave)

    self.add_request('SENSORS', self.get_sensors)
    self.add_request('PARAMS', self.get_params)
    self.add_request('RAW_VALUES', self.get_raw_values)

    self.add_request('battery', self.get_battery)

    self._update_lock = False
    self._last_command_source = 'startup'

  def update_device_config(self, **kwargs):
    self.node.refresh_info()
    self._config_updated = True

  def zwave_config(self, **kwargs):
    if self._node is None:
      logging.critical('FAILING TO UPDATE DEVICE')
      return False
    param = kwargs.get('id')
    value = kwargs.get('value')
    size = kwargs.get('size', 2)

    if size:
      size = int(size)

    if param and value:
      param = int(param)
      value = int(value)
      self._node.set_config_param(param, value, size=size)

    return True

  def export(self, current_values: bool = True, api_view: bool = False) -> dict:
    export_data = super().export(current_values, api_view)
    export_data['node_id'] = self._node_id
    export_data['manufacturer_id'] = self._manufacturer_id
    export_data['manufacturer_name'] = self._manufacturer_name
    export_data['product_name'] = self._product_name
    export_data['product_type'] = self._product_type
    export_data['battery'] = self._battery
    return export_data

  def get_sensors(self, **kwargs):
    sensor = kwargs.get('sensor')
    if sensor:
      s = self._sensors.get(sensor)
      return s
    return self._sensors

  def get_params(self, **kwargs):
    values = kwargs.get('VALUE')
    if values:
      s = self._config_params.get(values)
      return s
    return self._config_params

  def get_raw_values(self, **kwargs):
    values = kwargs.get('VALUE')
    if values:
      s = self._raw_values.get(values)
      return s
    return self._raw_values

  def update_from_zwave(self, node: ZWaveNode = None, ignore_update=False, **kwargs):
    '''
    Currently the update command is not in the COMMANDS -> THis is because it acts differently right now.. This may 
    change in the near future.
    Args:
      node ():

    Returns:

    '''

    logging.debug('Updating ZWave Values')

    # Return if no valid node object.
    if node is None:
      return

    try:
      if not self._manufacturer_id:
        self._manufacturer_id = node.manufacturer_id
      if not self._manufacturer_name:
        self._manufacturer_name = node.manufacturer_name
      if not self._product_name:
        self._product_name = node.product_name
      if not self._product_type:
        self._product_type = node.product_type
    except:
      pass

    values = kwargs.get('values')
    genre = ''
    if values is not None:
      genre = values.genre

    # This will set the node on the first update once zwave boots
    self._node = node
    self._node_id = node.node_id

    # Update config if device config has not been updated.
    if not self._config_updated:
      for s, i in node.get_values().items():
        if i.command_class == 112:
          self._config_params[i.label.lower()] = {
            'value': i.data,
            'id':    i.index
          }
        else:
          self._raw_values[i.label.lower()] = {
            'value': i.data,
            'id':    i.index,
            'class': i.command_class
          }
      self.update_device_config()

    # When security data changes sometimes you need to send a request to update the sensor value
    # old_security_data = [b for a, b in self._raw_values.items() if b.get('class') == 113]



    # for s, i in node.get_values().items():
    if genre == 'Config' or genre == 'System':
      if values.command_class == 112:
        self._config_params[values.label.lower()] = {
          'value': values.data,
          'id':    values.index
        }

    if genre == 'User':
      self._raw_values[values.label.lower()] = {
        'value': values.data,
        'id':    values.index,
        'class': values.command_class
      }

      if values.command_class == 128:
        self._battery = values.data

      for s, i in node.get_sensors().items():
        self._sensors[i.label.lower()] = i.data


        # new_security_data = [b for a, b in self._raw_values.items() if b.get('class') == 113]

        # If any of the security values change issue update command
        # if old_security_data != new_security_data:
        #  self._node.refresh_info()
        #  self._node.request_state()

  def get_battery(self):
    return self._battery

  @property
  def node(self):
    return self._node
