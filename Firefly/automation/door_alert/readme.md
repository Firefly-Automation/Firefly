# Door Alert
\[package: door_alert]

---

##### Description
Door Alert will flash selected lights 2 seconds on / 2 seconds off after a door is opened for more than X seconds.
It can also be setup to send you an alert message when the lights start flashing and stop flashing. 
The lights will be set back to their orginal state when it is stopped

##### Interface
- **devices.contact_censors**: List of doors/windows that will trigger the lights flashing.
- **delays.initial**: Wait this many seconds before flashing lights.
- **devices.lights**: Lights to flash for alert.
- **messages.initial**: Message to send when lights start/stop flashing.
- **messages.delayed**: Message to send when lights stop flashing.

---

**Author**: Zachary Priddy (me@zpriddy.com)