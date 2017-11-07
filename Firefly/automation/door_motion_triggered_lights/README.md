# Door/Motion Triggered Lights
\[package: door_motion_triggered_lights]

## About
This automation will set lights triggered from a motion event or a contact sensor event. 
It uses an OR based for the initial trigger and an AND based trigger for the secondary tigger.
It also accepts a delay for the secoandy trigger. 

## Example
Maybe you have a long hallway with a motion sensor or two and a door at the end of the hallway. 
You would  like the lights to turn on when there is motion in the hallway or when the door opens
at the end of the hallway. After 5 minutes of no motion and the door is closed you would like to have
the lights turn off. 

It uses OR logic for the start trigger so Motion Sensor 1 Active OR Motion Sensor 2 Active OR Door Opens will turn on the lights.

It then uses AND logic for the end trigger so Motion Sensor 1 Inactive AND Motion Sensor 2 Inactive And Door is closed.

## Inputs

- sensors.motion: list of motion sensors.
- sensors.doors: list of door sensors.
- lights.lights: turn on/off these lights.
- delays.off: seconds to delay before executing end action.

##### Advanced 

- commands.on: command to send to turn on lights. (defaults to {set_light:{on: true}})
- commands.off: command to send to turn off lights. (defaults to {set_light:{on: false}})
- actions.on: action to send on on command
- actions.off: action to send on off command


---

**Author**: Zachary Priddy (me@zpriddy.com)
