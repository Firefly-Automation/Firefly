# Routines
\[package: routine]

## About
Routines are a core part of Firefly, They act as your preset options. For example when you come home you may want the entry
lights to come on when the door opens and other lights to turn on. You may also want the mode to change to home and your 
thermostat to turn the heat on. You would make this your 'Home' routine. You could also have an 'Away' routine that turns everything
off as well as a 'Movie' routine that sets the lights for watching movies.

Like everything in firefly routines can act differently based on the sun, maybe you want different lights on during the day
than you do at night, or even maybe different light colors. Because of this routines give you a lot of options when setting them up. 

You can also define custom commands in the actions of the routines. (advanced)


## Inputs

- lights:
    - lights.on: a list of lights to turn on when the routine executes at any time.
    - lights.on_day: a list of lights to turn on when the routine executes when the sun is up.
    - lights.on_night: a list of lights to turn on when the routine executes when the sun is down.
    - lights.off: a list of lights to turn off when the routine executes at any time.
    - lights.off_day: a list of lights to turn off when the routine executes when the sun is up.
    - lights.off_night: a list of lights to turn off when the routine executes when the sun is down.

- commands:
    - commands.on: command to send to lights when turning them on. This defaults to ```{"set_light":{"switch":"on"}}```
    - commands.on_day: command to send to lights when turning them on when the sun is up. This defaults to ```{"set_light":{"switch":"on"}}```
    - commands.on_night: command to send to lights when turning them on when the sun is down. This defaults to ```{"set_light":{"switch":"on"}}```
    - commands.off: command to send to lights when turning them off. This defaults to ```{"set_light":{"switch":"off}}```
    - commands.off_day: command to send to lights when turning them off when the sun is up. This defaults to ```{"set_light":{"switch":"off"}}```
    - commands.off_night: command to send to lights when turning them off when the sun is down. This defaults to ```{"set_light":{"switch":"off"}}```

- simple_triggers:
    - triggers.contact_open: create a trigger when one of the contact sensors listed opens 
    - triggers.contact_closed: create a trigger when all of the contact sensors listed closes
    - triggers.motion_active: create a trigger when one of the motions sensors listed detects motion
    - triggers.motion_inactive: create a trigger when all of the motions sensors listed no longer detect motion
    - triggers.present: create a trigger when one of the presence devices listed are present
    - triggers.not_present: create a trigger when one of the presence devices listed are present
    - triggers.time
    - triggers.time_day (sunset, sunrise)
    - triggers.on
    - triggers.off
    - triggers.temp_above
    - triggers.temp_below

- triggers:
    - triggers.routine: (triggerList) that would cause the routine to execute.
    
- actions:
    - actions.routine: (commandList) custom action commands to send when the routine executes.
    
- conditions:
    - conditions.routine: (conditions) conditions for the routine executing.
    
- messages:
    - messages.routine: (string) message to send when the routine executes.
    
- icon:
    - icon.routine: (string) icon to show on the routine button in the web interface.
    
- export_ui:
    - export_ui.routine: (bool) Set true to display this routine on the web interface.

#### Notes
##### Commands
Lets say you have hue lights in your house, and you want them to be daylight during the day (6500K) you could set commands.on_day to: ```{"set_light":{"switch":"on","ct":6500}}```
You could also do the same thing for night at 2700K ```{"set_light":{"switch":"on","ct":2700}}```


##### Advanced 

- commands.on: command to send to turn on lights. (defaults to {set_light:{on: true}})
- commands.off: command to send to turn off lights. (defaults to {set_light:{on: false}})
- actions.on: action to send on on command
- actions.off: action to send on off command


---

**Author**: Zachary Priddy (me@zpriddy.com)
