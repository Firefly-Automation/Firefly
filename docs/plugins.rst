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


----------------
App Plugin
----------------