from openzwave.network import ZWaveNode

from Firefly import logging, scheduler
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadata.metadata import action_battery
from Firefly.util.zwave_command_class import COMMAND_CLASS_BATTERY, COMMAND_CLASS_DESC


class ZwavePrarmValue(object):
  #TODO: Maybe set better defaults
  def __init__(self, index=None, label=None, ref=None, value=None, command_class=None, value_type=None, genre=None):
    self.index = index
    try:
      self.label = self.label.lower()
    except:
      self.label = label
    self.ref = ref
    self.value = value
    try:
      self.command_class = COMMAND_CLASS_DESC[command_class]
    except:
      self.command_class = command_class
    self.type = value_type
    self.genre = genre



  def __repr__(self):
    return '<[ZWAVE VALUE] %(label)s: %(value)s [index: %(index)s, command class: %(command_class)s, genre: %(genre)s] %(ref)s>' % {
      'label': self.label,
      'value': self.value,
      'index': self.index,
      'command_class': self.command_class,
      'genre': self.genre,
      'ref': self.ref
    }


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

    self._node = kwargs.get('node')

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
    return_data = []
    for idx, value in self.zwave_values.items():
      return_data.append(value.__dict__)
    return return_data

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

    logging.debug('Updating ZWave Values: %s' % str(kwargs))

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
      for s, i in node.get_values().items():
        self.zwave_values["%s_%s" %(i.genre.lower(), i.index)] = ZwavePrarmValue(i.index, i.label, s, i.data, i.command_class, i.type, i.genre)
    elif kwargs.get('values'):
      values = kwargs.get('values')
      self.zwave_values["%s_%s" %(values.genre.lower(), values.index)] = ZwavePrarmValue(values.index, values.label, values.value_id, values.data, values.command_class, values.type, values.genre)


    if node.has_command_class(COMMAND_CLASS_BATTERY) and BATTERY not in self.request_map:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_battery())


    if self._node.is_ready and self._update_try_count <= 5 and not self._config_updated:
      scheduler.runInS(5, self.update_device_config, '%s-update_config' % self.id, max_instances=1)
    if self._update_try_count >6:
      self._config_updated = True
    logging.debug('Done updating ZWave Values')


  def get_battery(self):
    return self._battery

  def get_zwave_value(self, value_id: int) -> ZwavePrarmValue:
    try:
      return self.zwave_values[value_id]
    except KeyError:
      return ZwavePrarmValue()
    except Exception as e:
      logging.error('[ZWAVE DEVICE] unknown error: %s' % e)
      return ZwavePrarmValue()


  def verify_set_zwave_param(self, param_index, param_value, size=2) -> bool:
    if self.get_zwave_value("config_%s" %param_index) != param_value:
      self.node.set_config_param(param_index, param_value, size)
      return False
    return True

  def verify_set_zwave_params(self, param_list) -> bool:
    successful = True
    for param in param_list:
      if len(param) == 3:
        successful &= self.verify_set_zwave_param(param[0], param[1], param[2])
      elif len(param) == 2:
        successful &= self.verify_set_zwave_param(param[0], param[1])
      else:
        logging.error('[ZWAVE DEVICE] unknown param length')
    return successful

  @property
  def node(self):
    return self._node




