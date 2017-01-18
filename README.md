# Firefly Home Automation

## What is Firefly? 

Firefly is an opensource home automation system. It is light weight and can run off of a rasberryPi. The python based framework allows for easy development of apps and new components. Using this advanced framework Firefly is able to do complex actions in different scenarios.

Actions can be based off of time of day, if the sun is up, who is home, sensor state and anything else you can imagine!

For example my Hue lights fade from an orange to a daylight white either before my alarm goes off, or if its my day off, when the sun comes up. After I wake up the lights and the level of them are based off of a light sensor in each room, if its cloudy the lights are at 100%, if its sunny they are off, or if its partly cloudy they may be at 50%. At sunset the lights start to fade from the daylight white to a soft white and as it get closer to bedtime they go to a candle light. This is only one example of what can be done with Firefly.

Firefly has an open API that makes it easy to integrate with other systems allowing for seamless interactions such as the included ha-bridge functionality. 

## What deviecs are supported?

Voice commands using HA-Bridge (color commands not yet supported):

- Google Home
  - Hey Google, turn on kitchen lights
  - Hey Google, set lamp to 10%
- Alexa (Amazon Echo)
  - Alexa, turn on kitchen lights
  - Alexa, set lamp to 10%

Services:

- IFTTT
- Pushover (notifications)
- Locative (geofencing)

Devices:
- Hue Lights
- Nest
- Zwave sensors and switches

Partial Support:

- Lifx Lights*
- Ecobee*
- LG TV*

Coming Soon: 

- Chromecast
- Sonos
- Harmony Support (Using HA-Bridge)


## Requirements

- Dynamic DNS Service (Google Domains or DuckDNS.org) 
  - Currently working on other options but using the install script will only work if using dynamic DNS
- Port 443 forawrded to the IP of the RaspberryPi (This is for LetsEncrypt and Remote Access)


## Install Firefly

- Setup a raspberrypi with raspbian (GUI is Okay)
- Set timezone and keyboard settings in raspberry pi
- Set hostname of system (use the subdomain of the dynamic DNS domain as the hostname)
- Expand Filesystem $ sudo raspi-config
- Get install script $ wget https://raw.githubusercontent.com/zpriddy/Firefly/master/install_firefly.sh
- Run setup script $ sudo bash install_firefly.sh
