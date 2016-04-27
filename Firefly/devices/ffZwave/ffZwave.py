# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-24 17:40:36
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-26 22:56:16
from time import sleep, time
from sys import stdout
from core.models.device import Device
from core.models.event import Event as ffEvent
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
from core.models.command import Command as ffCommand

from louie import dispatcher, All
from core.scheduler import Scheduler
import logging

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'ZWave Controller',
      'author' : 'Zachary Priddy',
      'module' : 'ffZwave',
      'type' : 'zwave hub'
    }
    
    self.COMMANDS = {
      #'startup' : self.startup
      'switch' : self.switchNode
    }

    self.REQUESTS = {
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._port = str(args.get('port'))
    self._configFile = str(args.get('configFile'))
    self._oldData = {}
    self._network = None

    self._lastNodeUpdate = {}


    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

    
    self.startup()

  @property
  def name(self):
    return self._name
  

  def refreshData(self):
    #self.refresh_scheduler()
    logging.info('Refreshing Zwave Data')

  def startup(self, args={}):
    
    if self._network is None:
      self.install_zwave()
    self.get_all_node_data()
    self.refresh_scheduler()
    dispatcher.connect(self.testL, ZWaveNetwork.SIGNAL_VALUE_CHANGED)
    dispatcher.connect(self.testL, ZWaveNetwork.SIGNAL_NODE_EVENT)
    dispatcher.connect(self.testL, ZWaveNetwork.SIGNAL_SCENE_EVENT)
    dispatcher.connect(self.testL, ZWaveNetwork.SIGNAL_BUTTON_OFF)
    dispatcher.connect(self.testL, ZWaveNetwork.SIGNAL_BUTTON_ON)


  def testL(self, network, node):
    self.get_node_data(node._object_id)
    

  def install_zwave(self, args={}):
    ##Start the zwave network and wait for it to come on line
    logging.info('Installing Zwave')
    print 'Install Open Zwave'
    self._network = self.startup_zwave()
  

  def startup_zwave(self, args={}):
    ffEvent(self._id,{'zwave':'starting_up'})
    zwaveSetup = ZWaveOption(self._port, self._configFile)
    zwaveSetup.set_console_output(False)
    zwaveSetup.lock()
    network = ZWaveNetwork(zwaveSetup, autostart=False)
    network.start()

    stdout.write("Waking up Zwave (This can take up to 5 minutes)")
    for i in xrange(300):
      if network.state >= network.STATE_AWAKED:
        logging.info('Zwave Network Awake')
        break
      else:
        stdout.write(".")
        stdout.flush()
        sleep(1)

    for x in xrange(300):
      if network.state >= network.STATE_READY:
        ffEvent(self._id,{'zwave':'network_ready'})
      else:
        stdout.write(".")
        stdout.flush()
        sleep(.5)

    return network

  def get_all_node_data(self, args={}):
    if self._network is None:
      ffEvent(self._id,{'zwave':'network_not_ready'})
      logging.critical('Zwave not ready')
      return 1

    returnData = {}
    for node in self._network.nodes:
      nodeData = {}
      nodeData['node'] = node
      nodeData['manufacturer_name'] = self._network.nodes[node].manufacturer_name
      nodeData['product_name'] = self._network.nodes[node].product_name
      nodeData['product_id'] = self._network.nodes[node].product_id
      nodeData['product_type'] = self._network.nodes[node].product_type
      nodeData['device_type'] = self._network.nodes[node].device_type
      nodeData['command_classes_as_string'] = self._network.nodes[node].command_classes_as_string
      nodeData['ready'] = self._network.nodes[node].is_ready
      nodeData['failed'] = self._network.nodes[node].is_failed
      now = time()
      if self._lastNodeUpdate.get(node) is None or int(self._lastNodeUpdate.get(node) - now) > 1:
        for val in self._network.nodes[node].get_switches():
          self._network.nodes[node].refresh_value(val)
          self._lastNodeUpdate[node] = now
          sleep(1)
      dataValues = {}
      for a,b in self._network.nodes[node].values_to_dict().iteritems():
        dataValues[b['label']] = b

      nodeData['data'] = dataValues
      returnData['node-'+str(node)] = nodeData
      
    if self._oldData == returnData:
      logging.debug('Zwave No Change')
    else:
      chnageData = {}
      for oA, oB in self._oldData.iteritems():
        if oB != returnData[oA]:
          chnageData[oA] = returnData[oA]
          #logging.critical(str(returnData[oA]))
          ffCommand('zwave-' + str(oA), {'update' : returnData[oA]}, source='ffZwave')
      self._oldData = returnData

  def get_node_data(self, node):
    if self._network is None:
      ffEvent(self._id,{'zwave':'network_not_ready'})
      logging.critical('Zwave not ready')
      return 1

    returnData = {}
    
    nodeData = {}
    nodeData['node'] = node
    nodeData['manufacturer_name'] = self._network.nodes[node].manufacturer_name
    nodeData['product_name'] = self._network.nodes[node].product_name
    nodeData['product_id'] = self._network.nodes[node].product_id
    nodeData['product_type'] = self._network.nodes[node].product_type
    nodeData['device_type'] = self._network.nodes[node].device_type
    nodeData['command_classes_as_string'] = self._network.nodes[node].command_classes_as_string
    nodeData['ready'] = self._network.nodes[node].is_ready
    nodeData['failed'] = self._network.nodes[node].is_failed
    now = time()
    if self._lastNodeUpdate.get(node) is None or int(self._lastNodeUpdate.get(node) - now) > 2:
      for val in self._network.nodes[node].get_switches():
        self._network.nodes[node].refresh_value(val)
        self._lastNodeUpdate[node] = now
        sleep(.1)
    dataValues = {}
    for a,b in self._network.nodes[node].values_to_dict().iteritems():
      dataValues[b['label']] = b

    nodeData['data'] = dataValues
    returnData = nodeData

    #logging.critical(returnData)
      
    if self._oldData['node-'+str(node)] == returnData:
      logging.debug('Zwave No Change')
    else:
      if self._oldData['node-'+str(node)] != returnData:
        ffCommand('zwave-' + str('node-'+str(node)), {'update' : returnData}, source='ffZwave')
      self._oldData['node-'+str(node)] = returnData

  def refresh_scheduler(self, args={}):
    logging.debug("Starting Zwave Scheduler")
    zwaveRefresh = Scheduler()
    zwaveRefresh.runEveryS(10,self.get_all_node_data,replace=True,uuid='ZwaveRefresher')

  #########################################################################################
  #           ACTIONS
  #########################################################################################
  def switchNode(self, args={}):
    nodeID = args.get('node')
    switchID = args.get('switchID')
    state = args.get('on')
    logging.critical('Switching Node ' + str(nodeID))

    if nodeID is None or state is None:
      return -1

    if switchID is None:
      for val in self._network.nodes[nodeID].get_switches():
        self._network.nodes[nodeID].set_switch(val, state)
    else:
      self._network.nodes[nodeID].set_switch(switchID, state)
