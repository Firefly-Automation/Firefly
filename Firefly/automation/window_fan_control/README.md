# Window Fan Control
\[package: window_fan_control]

## About
This automation plugin is to control the temperature of a room or your whole house using window fans.
The idea is when it is colder outside and you open your windows and place a window fan in the window, you
can target a temperature that you would like the room to be. If it hits the lower limit of the range it 
will turn off the fans. If it hits the higher limit of the range it will turn the fans back on. 


### Future Plans
Pull in weather data as well as inside data.


## Inputs

- sensors.temperature: list of temperature sensors.
- sensors.windows: list of windows sensors that must be open for actions to happen.
- switches.fans: turn on/off these fans.
- delays.off: seconds to delay before turning off fans once temperature hits lower limit.
- delays.on: seconds to delay before turning on fans once temperature hits higher limit.



---

**Author**: Zachary Priddy (me@zpriddy.com)