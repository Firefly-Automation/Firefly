Foobot Plugin
====

The Foobot plugin is for the Foobot Air Quality Sensor [foobot.io](https://foobot.io)

All readings from the Foobot API are available in Firefly. They can be used to trigger automation or alerts.

On startup the plugin will discover all Foobot devices that you have linked to your account. 
These devices will refresh every 15 minutes by default but this interval can be changed. 
Every 2 hours it will look for any new devices in your account and add them to Firefly.

**Service Packages**: 
* Firefly.components.foobot.foobot_service

**Device Packages**: 
* Firefly.components.foobot.foobot: Foobot Device

Requests
---
* temperature: Current temperature
* air_quality: Calculated air quality reading. These numbers were taken from the Foobot app.
* pm: Particulate Matter (ug/m^3)
* c02: Carbon Dioxide (ppm)
* voc: Volatile Organic Compounds (ppb)
* allpillu: All Pollutants

Commands
---
* set_scale : set_scale:{scale: c/f} Change the temperature between C/F

Config & Setup
---
To setup foobot first you must get an api_key from: https://api.foobot.io/apidoc/index.html and click 'Request API Key'

**Service Config Section**: [FOOBOT]
* enable: true/false enable foobot service
* api_key: api key from foobot website
* username: email address you use to login to foobot
* refresh_interval: (optional) How often to refresh foobot data. Defaults to 15 min. 15 min is good for 2 devices. There is a max of 200 calls per day.
* package:'Firefly.components.foobot.foobot_service'