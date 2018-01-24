# Firefly Home

## What is Firefly? 

Firefly is an open-source home automation system, This system has been a passion of mine for about 5 years now and wll here it is. 
There is an option (really at this time the only way to make it usable) for cloud based control using Firebase. Before setting up your Firefly system
you will need to go to [https://my.firefly-home.io](https://my.firefly-home.io) and create an account. Please note that all automation actions are done
locally on the raspberryPi and the cloud support is for remote control, Alexa, Google Home, and Facebook Messenger support, it is also used for geofence 
reporting using OwnTracks. 

There has been a full plugin framework developed for Devices, Services, and Automation and soon to come full documentation for how Firefly operates. 

For setup you can just run the setup.sh scrip on your raspberryPi and it will take you though the setup process. To enable cloud support, 
after setting up your raspberryPi you will need to create a file '/opt/firefly_system/Firefly/dev_config/services.firebase.json' with the 
email and password used to create your account at mMy.Firefly-Home.io
```json
{
    "username": "email@gmail.com",
    "password": "mySecurePassword"
}
```

After doing this run:
```bash 
sudo service firefly restart
```

Your new firefly system will register with the server automatically and within minutes you will be able to see it on the website. 
After doing so you will be able to install enable services and add devices and automation (coming soon)

You can also add automation and services by editing the files in the dev_config folder mentioned above. There are samples of how to do this in the
sample_config fodler of this repo.


## Supported
- Google Home
- Amazon Echo / Alexa
- Facebook Messenger
- Pushover
- OwnTracks
- Hue
- Lightify
- Zwave
- DarkSky
- Nest
- Foobot

## Prebuilt Automation
Look under Firefly/automation in this repo. Each automation should have a README explaining what it does.
- Routines
- Door/Motion Lights
- Window Fan Control
- Nest Eco Window
- Door Alert


pip install git+https://github.com/vaab/colour