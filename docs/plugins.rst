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

  from core.models.device import Device
  import logging

  class Device(Device):
    def __init__(self, deviceID, args={}):
      self.METADATA = {
        'title' : 'Plugin Title',
        'type' : 'Plugin Type',
        'package' : 'FOLDER NAME OF PLUGIN',
        'module' : 'FILE NAME OF PLUGIN'
      }
      
      self.COMMANDS = {
        'command' : self.function
      }

      self.REQUESTS = {
        'request' : self.function
      }
      args = args.get('args')
      name = args.get('name')
      super(Device,self).__init__(deviceID, name)

    # Your Code Goes Here


Sample Device
---------------
.. code-block :: python

   from core.models.device import Device
  import logging

  class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Presence Device',
      'type' : 'presence',
      'package' : 'ffPresence',
      'module' : 'ffPresence'
    }
    
    self.COMMANDS = {
      'presence' : self.setPresence
    }

    self.REQUESTS = {
      'presence' : self.getPresence
    }
    args = args.get('args')
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)

    self._notify_present = args.get('notify_present')
    self.notify_not_present = args.get('notify_not_present')
    self.notify_device = args.get('notify_device')
    self._presence = True

  def setPresence(self, value):
    from core.firefly_api import event_message
    if value is not self.presence:
      self.presence = value
      event_message(self._name, "Setting Presence To " + str(value))
      logging.debug("Setting Presence To " + str(value))
      

  def getPresence(self):
    return self.presence

  @property
  def presence(self):
      return self._presence

  @presence.setter
  def presence(self, value):
    self._presence = value


Device With Children
--------------------
Part 1: Installer
#################

   
Part 2: Background High Speed Refresh
#####################################
Most devices will not need something like this. This was an example of a high speed refresher polling form an external API every two seconds for changes. 

.. code-block :: python


----------------
App Plugin
----------------