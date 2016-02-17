========
Plugins
========

There are two different types of plugins:
   - Device Plugin
   - App Plugin

Plugins have a small set of required functions and libraries in order to function correcly. Besides these required functions there are no limits on what can be used with them. Below there are sample templates for the different plgin types. 

**NOTE: We do suggest using treq instead of requests to keep things running faster.**

Difference between device plugin and app plugin:

Device Plugin:
   - Can reviece commands
   - Can send events to the Firefly controller

App Plugin:
   - Can receive events. (ie triggers)
   - Can subscribe to events from devices

----------------
Device Plugin
----------------

There are two parts to the device plugins:
   1. The device its self
   2. The device installer script

Device installer scripts can be used to install more than just one device. i.e: SmartThings installer script installs various device types using a common smartthings libary. By doing this the installer script sets up a refresh loop to refresh all devices that it installed.  

Device Template
----------------
**NOTE: It is suggested to keep a 'getValue' function as shown in the sample device blow, But it is not required.**

.. code-block :: python

   metadata = {
     'title' : '<<DEVICE TITLE>>',
     'author' : '<<DEVICE AUTHOR>>',
     'commands' : [<<LIST OF DEVICE COMMANDS>>],
     'capabilities' : [<<LIST OF CAPABILITIES>>],
   }

   class Device(object):
     def __init__(self, pid):
       self.id = pid
       self.metadata = metadata
       self._commands = {}
       self.update()
       self._st_device = {}

     def update(self):
       self._commands = {
       '<<COMMAND FROM LIST OF COMMANDS>>': self.<<COMMAND>>,
       'off': self.off,
       'setLevel': self.setLevel,
       'getValue': self.getValue
       }

     def command(self, args={}):
       command = args['command']
       """This method should not be changed - This is how commands are executed"""
       if command in self._commands:
         return self._commands[command](args)
       else:
         return False

Sample Device
---------------
.. code-block :: python

   import zPySmartThings_lib as st

   metadata = {
     'title' : 'zPySmartThings Dimmer Device',
     'author' : 'zpriddy',
     'commands' : ['on', 'off', 'setLevel', 'getValue'],
     'capabilities' : ['switch','level'],
   }

   class Device(object):
     def __init__(self, pid):
       self.id = pid
       self.metadata = metadata
       self._commands = {}
       self.update()
       self._st_device = {}

     def update(self):
       self._commands = {
       'on': self.on,
       'off': self.off,
       'setLevel': self.setLevel,
       'getValue': self.getValue
       }

     def command(self, args={}):
       command = args['command']
       """This method should not be changed - This is how commands are executed"""
       if command in self._commands:
         return self._commands[command](args)
       else:
         return False

     ## START OF PLUGIN CODE ##


     #This is used by the installer script
     def set_device(self, args={}):
       #args should include {'st_device': {'id':'Kitchen Lights','type':dimemr}}
       self._st_device = args
       self.update()

     def on(self, args={}):
       cmd = st.command_switch(self._st_device['id'], 'on')
       if cmd['error'] == 0:
         return True
       return False

     def off(self, args={}):
       cmd = st.command_switch(self._st_device['id'], 'off')
       if cmd['error'] == 0:
         return True
       return False

     def setLevel(self, args={}):
       level = args['level']
       cmd = st.command_dimmer(self._st_device['id'], level)
       if cmd['error'] == 0:
         return True
       return False

     def getValue(self, args={}):
       item = args['item']
       if item == 'switch' or item == 'level':
         state = st.getDimmer()[self._st_device['id']]
         return state
       return False

Sample Installer
----------------
Part 1: Installer
#################
.. code-block :: python
   
   ## THESE ARE REQUIRED
   from core.core_api import firefly_scheduler
   from core.firefly_plugin_controller import devices
   from core.utils import send_event
   from core.utils import send_direct_event
   import logging
   ##

   from config.zPySmartThings_settings import settings
   import zPySmartThings_lib as st
   import zPySmartThings_switch_device as switch_device
   import zPySmartThings_dimmer_device as dimmer_device
   import zPySmartThings_motion_device as motion_device
   import zPySmartThings_contact_device as contact_device

   import time
   import treq

   before = {}

   metadata = {
     'type' : 'installer',
     'title' : 'zPySmartThings Installer',
     'author' : 'Zachary Priddy'
   }

   class Installer(object):
     def __init__(self):
       logging.basicConfig(level=logging.DEBUG)
       pass

     def install(self, *config):
       plugin_devices = {}
       if config[0]['st_device']['type'] == 'switch':
         #print 'Switch'
         plugin_device= switch_device.Device(config[0]['id'])
         plugin_device.set_device(config[0]['st_device'])
         plugin_devices[config[0]['id']] = plugin_device

       if config[0]['st_device']['type'] == 'dimmer':
         #print 'Dimmer'
         plugin_device= dimmer_device.Device(config[0]['id'])
         plugin_device.set_device(config[0]['st_device'])
         plugin_devices[config[0]['id']] = plugin_device

       if config[0]['st_device']['type'] == 'motion':
         #print 'Motion'
         plugin_device= motion_device.Device(config[0]['id'])
         plugin_device.set_device(config[0]['st_device'])
         plugin_devices[config[0]['id']] = plugin_device

       if config[0]['st_device']['type'] == 'contact':
         #print 'Motion'
         plugin_device= contact_device.Device(config[0]['id'])
         plugin_device.set_device(config[0]['st_device'])
         plugin_devices[config[0]['id']] = plugin_device

       

       firefly_scheduler.runInS(5, poll_devices, replace=True, uuid='STScheduleRefresh')

       return plugin_devices
   
Part 2: Background High Speed Refresh
#####################################
Most devices will not need something like this. This was an example of a high speed refresher polling form an external API every two seconds for changes. 

.. code-block :: python
   
   ###############################################################################
   # This is the device refresh loop. I use treq here so that the twisted        #
   # framework can run in the background like a threading proccess and not hold  #
   # up the whole system like requests would done                                #
   #                                                                             #
   # 1st - The poll_devices is call that makes the request to smartthings        #
   # 2nd - Once the data is recived it then sends it to devices_callback. This is#
   #       where the json data is pulled out and then passed onto body_recived.  #
   # 3rd - body_recieved gets the data sends it to the ST lib where is it stored #
   #       in a variable and then compairs the last result to the current result #
   #       if there are any changes it then posts an send_event command. After   #
   #       this is done it then schedules a new poll_devices with a small delays #
   #                                                                             #
   # This chnage is so that no more than one poll is called at a time. It also   #
   # prevents data from being writen while trying to read the data and cause     #
   # errors and longer delays.                                                   #
   ###############################################################################

   def devices_callback(response):
     deferred = treq.json_content(response)
     deferred.addCallback(body_received)

   def body_received(body):
     global before

     st.devices(body)

     after = {}
     for name, value in devices.iteritems():
       if 'SmartThings' in value.metadata['title']:
         after[name] = {}
         for item in value.metadata['capabilities']:
           try:
             after[name][item] = value.getValue({'item':item})
           except:
             print 'Error getting device'

     if before:
       if before != after:
         for item in before:
           if before[item] != after[item]:
             print item
             print after[item]
             #send_event(item, after[item])
             send_direct_event(item, after[item])


     before = after

     firefly_scheduler.runInS(1, poll_devices, replace=True, uuid='SmartThingsPollDevices')

   def poll_devices(url_path='devices', device_id=None, callback=devices_callback):
     """List the devices"""

     devices_url = "%s/%s" % ( settings["url"], url_path )
     devices_paramd = {
       "deviceId":device_id,
     }
     devices_headerd = {
       "Authorization": "Bearer %s" % settings["access_token"],
     }

     treq.get(url=devices_url, headers=devices_headerd, json=devices_paramd).addCallback(callback)


----------------
App Plugin
----------------