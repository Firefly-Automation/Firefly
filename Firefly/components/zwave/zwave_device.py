from openzwave.network import ZWaveNode

from Firefly import logging, scheduler
from Firefly.helpers.device.device import Device
from Firefly.helpers.device import *
from Firefly.helpers.metadata import action_battery
from Firefly.util.zwave_command_class import COMMAND_CLASS_BATTERY


class ZwaveDevice(Device):
  def __init__(self, firefly, package, title, author, commands, requests, device_type, **kwargs):

    #commands.append('ZWAVE_CONFIG')
    #commands.append('ZWAVE_UPDATE')

    #requests.append('SENSORS')
    #requests.append('PARAMS')
    #requests.append('RAW_VALUES')
    #requests.append('ZWAVE_VALUES')
    #requests.append('battery')

    super().__init__(firefly, package, title, author, commands, requests, device_type, **kwargs)

    self._node: ZWaveNode = kwargs.get('node')

    self._sensors = {}
    self._switches = {}
    self._config_params = {}
    self.zwave_values = {}
    self._raw_values = {}
    self._config_updated = False
    self._update_try_count = 0
    self._node_id = kwargs.get('node_id')

    self._manufacturer_id = ''
    self._manufacturer_name = ''
    self._product_name = ''
    self._product_type = ''

    self.value_map = kwargs.get('value_map', {})



    self.add_command('ZWAVE_CONFIG', self.zwave_config)
    self.add_command('ZWAVE_UPDATE', self.update_from_zwave)

    #self.add_request('SENSORS', self.get_sensors)
    #self.add_request('PARAMS', self.get_params)
    #self.add_request('RAW_VALUES', self.get_raw_values)
    self.add_request('ZWAVE_VALUES', self.get_zwave_values)

    self._battery = kwargs.get('battery', 'NOT REPORTED')
    #self.add_request('battery', self.get_battery)
    #self.add_action('battery', metaText(text_request='battery', context='Current Battery Level', title='Battery'))

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
    export_data['value_map'] = self.value_map
    return export_data

  def get_zwave_values(self, **kwargs):
    return self.zwave_values

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
    if node is None and self._node is None:
      return

    if node is None:
      node = self._node

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


    # This will set the node on the first update once zwave boots
    self._node = node
    self._node_id = node.node_id

    # Update config if device config has not been updated.
    if not self._config_updated:
      try:
        for s, i in node.get_values().items():
          self.zwave_values[i.index] = {
            'label': i.label.lower(),
            'class': i.command_class,
            'value': i.data,
            'ref': s,
            'index': i.index,
            'genre': i.genre,
            'type': i.type
          }
      except:
        pass

    if node.has_command_class(COMMAND_CLASS_BATTERY) and BATTERY not in self.request_map:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_battery())

    scheduler.runInS(5, self.update_device_config, '%s-update_config' % self.id, max_instances=1)
    logging.debug('Done updating ZWave Values')


  def get_battery(self):
    return self._battery

  @property
  def node(self):
    return self._node
