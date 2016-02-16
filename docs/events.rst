######
Events
######

----------------------
Standard Event Format
----------------------

This is how event messages should be formatted: 

.. code-block:: python

   {'dimmer':{'state':'on', 'level':'100'}}

This should follow the format of:

.. code-block:: python

   {'EVENT DEVICE TYPE': {'EVENT VAR': 'EVENT VAL'}}


--------------------
Sending an Event
--------------------

**NOTE: In next release send_direct_event will be replaced with send_event**

All files that require sending an event should follow the format:

.. code-block:: python

   from core.untils import send_direct_event

   ...

   send_direct_event(<<DEVICE>>, <<EVENT IN STANDARD EVENT FORMAT>>)


Sample Event:

.. code-block:: python

   from core.utils import send_direct_event

   ...

   send_direct_event('Kitchen Motion', {'motion':{'state':'active'}})
