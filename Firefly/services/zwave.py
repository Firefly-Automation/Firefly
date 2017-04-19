import asyncio
import configparser
import json

from openzwave.network import ZWaveNetwork, dispatcher, ZWaveController
from openzwave.option import ZWaveOption

from Firefly import logging
from Firefly import scheduler
from Firefly.const import SERVICE_CONFIG_FILE, ZWAVE_FILE
from Firefly.helpers.events import Command
from Firefly.helpers.service import Service

PACKAGE_MAPPING = {
  'ZW096 Smart Switch 6': 'zwave_aeotec_smart_switch_gen_6',
  'DSC06106 Smart Energy Switch': 'zwave_aeotec_dsc06106_smart_switch',
  'ZW100 MultiSensor 6': 'zwave_aeotec_multi_6',
  'ZW120 Door Window Sensor Gen5': 'zwave_aeotec_door_window_gen_5',
  'ZW097 Dry Contact Sensor Gen5': 'zwave_aeotec_zw097_dry_contact',
  '12730 Fan Control Switch': 'zwave_ge_12724_dimmer',
  '12729 3-Way Dimmer Switch': 'zwave_ge_12724_dimmer',
  '12724 3-Way Dimmer Switch': 'zwave_ge_12724_dimmer'
}
CONFIG_MAPPING = {
  'ge/12724-dimmer.xml': 'zwave_ge_12724_dimmer'
}


'''
The ZWAVE service is the background service for zwave.

There will be a zwave device class in the zwave device folder. This class will handle actions
like sending commands to the zwave service. This by using this device class we can easily make
new zwave devices.

Zwave service should automatically create child devices from the device type that the zwave
service detects from that node ID. These devices can later be customized to custom device types.

All zwave devices will be IDed by their serial number if possible but will also have to keep tack
of what node number they are for sending commands.
'''

TITLE = 'Z-Wave service for Firefly'
AUTHOR = 'Zachary Priddy me@zpriddy.com'
SERVICE_ID = 'service_zwave'
COMMANDS = ['send_command', 'stop', 'add_node', 'cancel']
REQUESTS = ['get_nodes', 'get_orphans']

SECTION = 'ZWAVE'
STARTUP_TIMEOUT = 10


def Setup(firefly, package, **kwargs):
  logging.message('Setting up %s service' % SERVICE_ID)
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)

  enable = config.getboolean(SECTION, 'enable', fallback=False)
  port = config.get(SECTION, 'port', fallback=None)
  # path = config.get(SECTION, 'path', fallback='/opt/firefly_system/python-openzave')
  path = config.get(SECTION, 'path', fallback=None)
  if not enable or port is None:
    return False

  try:
    with open(ZWAVE_FILE) as f:
      zc = json.loads(f.read())
      installed_nodes = zc.get('installed_nodes')
      if installed_nodes:
        kwargs['installed_nodes'] = installed_nodes
      print('INSTALLED NODES = %s' % str(installed_nodes))
  except Exception as e:
    print('ZWAVE ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s' % e)
    pass

  zwave = Zwave(firefly, package, enable=enable, port=port, path=path, **kwargs)
  firefly.components[SERVICE_ID] = zwave
  return True


class Zwave(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self._port = kwargs.get('port')
    self._path = kwargs.get('path')
    self._path = '/opt/firefly_system/python-openzwave/openzwave/config'
    self._enable = kwargs.get('enable')
    self._zwave_option = None
    self._network: ZWaveNetwork = None
    self._installed_nodes = kwargs.get('installed_nodes', {})

    # TODO: Enable zwave security
    self._security_enable = True

    self.add_command('send_command', self.send_command)
    self.add_command('stop', self.stop)
    self.add_command('add_node', self.add_device)
    self.add_command('cancel', self.cancel_command)

    self.add_request('get_nodes', self.get_nodes)
    self.add_request('get_orphans', self.get_orphans)

    scheduler.runInS(5, self.initialize_zwave)

    # TOD: REMOVE THIS
    self.count = 0

  async def initialize_zwave(self):
    if self._network is not None:
      return False
    self._zwave_option = ZWaveOption(self._port, self._path)
    self._zwave_option.set_console_output(False)
    self._zwave_option.lock()

    self._network = ZWaveNetwork(self._zwave_option, autostart=False)
    self._network.start()

    logging.message('Starting ZWAVE - This can take up to 5 minutes.. Will notify when finished')

    for i in range(STARTUP_TIMEOUT):
      if self._network.state >= self._network.STATE_AWAKED:
        logging.message('ZWAVE is awake')
        break
      else:
        await asyncio.sleep(1)

    for i in range(STARTUP_TIMEOUT):
      if self._network.state >= self._network.STATE_READY:
        logging.message('ZWAVE is ready')
        break
      else:
        await asyncio.sleep(1)

    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NODE_ADDED)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_BUTTON_OFF)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_BUTTON_ON)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NODE)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NODE_EVENT)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE_REFRESHED)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_ALL_NODES_QUERIED)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_CONTROLLER_COMMAND)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_SCENE_EVENT)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_GROUP)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_CONTROLLER_WAITING)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NOTIFICATION)
    # dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE_CHANGED)
    dispatcher.connect(self.new_node, ZWaveNetwork.SIGNAL_NODE_ADDED)

    self._network.set_poll_interval(milliseconds=500)

  def stop(self):
    self.export()
    self._network.stop()

  def zwave_handler(self, *args, **kwargs):
    print(kwargs)
    print(str(kwargs.get('value')))
    print('**** genre: ' + str(kwargs.get('value').genre))
    if kwargs.get('node') is None:
      logging.critical('********************\n*************')
      logging.critical(kwargs)
      return

    if type(kwargs.get('node')) is ZWaveController:
      return

    logging.debug('zwave change received %s' % kwargs.get('node').node_id)
    node_id = str(kwargs.get('node').node_id)
    print(self._installed_nodes)
    if node_id not in self._installed_nodes:
      node = kwargs.get('node')
      try:
        self.add_child_nodes(node)
      except Exception as e:
        logging.error('[zwave] error installing node %s: %s' % (node, e))

    elif self._installed_nodes[node_id] not in self._firefly.components:
      self._installed_nodes.pop(node_id)
      node = kwargs.get('node')
      try:
        self.add_child_nodes(node)
      except:
        logging.error('[zwave] error installing node %s' % node)


        # TODO: Change this to a send_command -> This will then do an update and broadcast
        # TODO: Pass all kwargs not just node

    else:
      node = kwargs.get('node')
      values = kwargs.get('value')
      command = Command(self._installed_nodes[node_id], SERVICE_ID, 'ZWAVE_UPDATE', node=node, values=values)
      try:
        self._firefly.send_command(command)
      except Exception as e:
        logging.error('[zwave] Error sending command: %s' % e)
        # self._firefly.components[self._installed_nodes[node_id]].update_from_zwave(node, values=values)

  def add_child_nodes(self, node):
    node_id = str(node.node_id)
    product_name = node.product_name
    config = 'node.config'

    print('******************************************')
    print(node_id)
    print(node.to_dict())
    print(node.device_type)
    print(product_name)
    print(node.manufacturer_id)
    print(node.manufacturer_name)
    print('******************************************')

    if product_name in PACKAGE_MAPPING:
      package = 'Firefly.components.zwave.%s' % PACKAGE_MAPPING[product_name]
      device_id = self._firefly.install_package(package, alias=product_name, node=node)
      self._installed_nodes[node_id] = device_id

    elif config in CONFIG_MAPPING:
      package = 'Firefly.components.zwave.%s' % CONFIG_MAPPING[config]
      device_id = self._firefly.install_package(package, alias=product_name, node=node)
      self._installed_nodes[node_id] = device_id

    elif 'On/Off Power Switch' in node.device_type  or 'On/Off Relay Switch' in node.device_type:
      device_id = self._firefly.install_package('Firefly.components.zwave.zwave_switch', alias=node.device_type, node=node)
      self._installed_nodes[node_id] = device_id

    elif 'On/Off Power Switch' in product_name  or 'On/Off Relay Switch' in product_name:
      device_id = self._firefly.install_package('Firefly.components.zwave.zwave_switch', alias=product_name, node=node)
      self._installed_nodes[node_id] = device_id

    elif 'Door/Window Sensor' in product_name:
      device_id = self._firefly.install_package('Firefly.components.zwave.window_door_sensor', alias=product_name, node=node)
      self._installed_nodes[node_id] = device_id

    else:
      print('******************************************')
      print(node_id)
      print(node.to_dict())
      print(node.device_type)
      print(product_name)
      print(node.manufacturer_id)
      print(node.manufacturer_name)
      print('******************************************')

    self.export()

  def export(self):
    with open(ZWAVE_FILE, 'w') as f:
      json.dump({'installed_nodes': self._installed_nodes}, f, sort_keys=True, indent=4)

  def new_node(self, *args, **kwargs):
    logging.notify('New Node Added: %s' % kwargs)
    pass

  def add_device(self, **kwargs):
    '''
    Hope we can add pairing mode
    Returns:

    '''
    from time import sleep
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&& %s' % kwargs)
    security = self._security_enable
    if kwargs.get('security'):
      security = True if kwargs.get('security') == 'true' else False
    #tries = 0
    #while self._network.controller.is_locked and tries < 30:
    #  logging.info('sleeping while zwave is locked. security_enabled=%s' % security)
    #  sleep(1)
    #  tries += 1
    #if tries >= 30:
    #  logging.notify('error unlocking zwave. Try again.')
    #  return
    logging.notify('Ready to pair zwave device.')
    logging.info('adding zwave: security: %s' % security)
    return self._network.controller.add_node(doSecurity=security)

  def cancel_command(self):
    """
    Cancels the zwave command (This is how you would stop pairing mode etc..) Maybe this should get called when a new node
    notification is sent. This would make it so you can only add one device at a time.. Good thing?
    Returns:

    """
    self._network.controller.cancel_command()
    return True

  def remove_device(self):
    '''
    Hope we can add remove device mode
    Returns:

    '''
    self._network.controller.remove_node()

  def send_command(self):
    '''
    Function that zwave devices call when sending a command
    Returns:

    '''
    pass

  def get_update(self):
    '''
    This is the function that is called when updates for zwave are received. This function will
    then send updates to the child devices that updates were received for.
    Returns:

    '''
    pass

  def get_nodes(self):
    '''
    Get a list of nodes (nodeID, device serial, and device type)
    Returns:

    '''
    pass

  def get_orphans(self):
    '''
    Get a list of nodes that are orphaned and not in the alias file
    Returns:

    '''
    pass
