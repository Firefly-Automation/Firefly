# Firefly 


# NOTE: This is currently in development


## What is Firefly? 

Firefly is a python based open source home automation system. It is desigend to run on a raspberrypi, however it can run on anything and even on a docker image. 

Firefly has a very easy to use plugin framework that allows you to make plugins for devices as well as applications. (To be documented)

Firefly has an easy to use Web based UI and a token based API

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
- Pushover
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
- Port 443 forawrded to the IP of the RaspberryPi (This is for LetsEncrypt and Remote Access)


## Install Firefly

- Setup a raspberrypi with raspbian (GUI is Okay)
- Expand Filesystem $ sudo raspi-config
- Get install script $ wget https://raw.githubusercontent.com/zpriddy/Firefly/master/install_firefly.sh
- Run setup script $ sudo bash install_firefly.sh
