=========
Config
=========

---------------------
Firefly Config Files
---------------------
There are multiple Firefly config files:

* firefly.confg
* devices.json
* routine.json
* apps.json
* app_config
  
  * APP NAME

    * config.json



-------------
firefly.json
-------------

.. code-block :: text

  [FIREFLY]
  host: localhost
  port: 6002

  [USER]
  username: admin
  password: FFPassword123

  [LOCATION]
  zipcode: 95110
  modes: [home, away, night, art-mode, vacation]

There are three sections to this config file:

* FIREFLY
  
  Address and port to run the Firefly backend.

* USER

  Inital Admin username and password.

* LOCATION

  Zipcode of home - used for timing.

  Modes: Available modes to set the system into.


-------------
devices.json
-------------

Look at sample

-------------
routine.json
-------------

Look at sample

-------------
apps.json
-------------

Look at sample
