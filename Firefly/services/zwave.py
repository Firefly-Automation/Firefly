import configparser
from Firefly import scheduler


import asyncio
from openzwave.network import ZWaveNetwork, ZWaveNode, dispatcher
from openzwave.option import ZWaveOption

from Firefly import logging
from Firefly.const import SERVICE_CONFIG_FILE
from Firefly.helpers.service import Service

from time import sleep

#from pydispatch import dispatcher

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
COMMANDS = ['send_command']
REQUESTS = ['get_nodes', 'get_orphans']

SECTION = 'ZWAVE'
STARTUP_TIMEOUT = 10

def Setup(firefly, package, **kwargs):
  logging.message('Setting up zwave service')
  config = configparser.ConfigParser()
  config.read(SERVICE_CONFIG_FILE)

  enable = config.getboolean(SECTION, 'enable', fallback=False)
  port = config.get(SECTION, 'port', fallback=None)
  #path = config.get(SECTION, 'path', fallback='/opt/firefly_system/python-openzave')
  path = config.get(SECTION, 'path', fallback=None)
  if not enable or port is None:
    return False

  zwave = Zwave(firefly, package, enable=enable, port=port, path=path, **kwargs)
  firefly.components[SERVICE_ID] = zwave
  return True

class Zwave(Service):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, SERVICE_ID, package, TITLE, AUTHOR, COMMANDS, REQUESTS)

    self._port = kwargs.get('port')
    self._path = kwargs.get('path')
    self._enable = kwargs.get('enable')
    self._zwave_option = None
    self._network = None
    self._installed_nodes = {}

    self.add_command('send_command', self.send_command)

    self.add_request('get_nodes', self.get_nodes)
    self.add_request('get_orphans', self.get_orphans)

    scheduler.runInS(1,self.initialize_zwave)




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


    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE_CHANGED)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_BUTTON_OFF)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_BUTTON_ON)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NODE)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_NODE_EVENT)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE_REFRESHED)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_VALUE)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_ALL_NODES_QUERIED)
    dispatcher.connect(self.zwave_handler, ZWaveNetwork.SIGNAL_CONTROLLER_COMMAND)

    #self._network.set_poll_interval(milliseconds=500)

    #print(self._network.controller.request_controller_status())

    #scheduler.runEveryS(10, self.print_nodes)


  def print_nodes(self):
    s = self._network.nodes[8]
    for a, b in s.get_switches().items():
      print(b)
      print(b.data)
      #if b.data:
      #  self._network.switch_all(0)
      #else:
      #  self._network.switch_all(1)

    for a, b in s.get_sensors().items():
      print(b)

    #s.set_config_param(255,1)
    #s.set_config_param(80, 1)
    #s.set_config_param(100, 5)
    #s.set_config_param(110, 5)
    #s.set_config_param(103, 15)
    #s.set_config_param(102, 15)
    #s.set_config_param(101, 15)
    #s.set_config_param(112, 5)
    #s.set_config_param(112, 5)
    #s.set_config_param(113, 5)
    #s.set_config_param(90, 1)



  def zwave_handler(self, *args, **kwargs):
    logging.debug('zwave change received %s' % kwargs.get('node').node_id)
    node = kwargs.get('node').node_id
    if node not in self._installed_nodes:
      self.add_child_nodes(kwargs.get('node'))

    self._firefly.components[self._installed_nodes[node]].update_from_zwave(kwargs.get('node'))

  def add_child_nodes(self, node):
    #self._firefly.insatll_package
    if node.device_type == 'On/Off Power Switch':
      device_id = self._firefly.install_package('Firefly.components.zwave.zwave_switch', alias='zwave_switch', node=node)
      self._installed_nodes[node.node_id] = device_id


  def add_device(self):
    '''
    Hope we can add pairing mode
    Returns:

    '''
    pass

  def remove_device(self):
    '''
    Hope we can add remove device mode
    Returns:

    '''
    pass

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

