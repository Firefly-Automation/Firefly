INTERFACE = {
  'secure_motion_enabled':  {
    'type':    'modeList',
    'context': 'Modes that the security system should be armed and monitoring motion for. (i.e. Away)'
  },
  'secure_motion_disabled': {
    'type':    'modeList',
    'context': 'Modes that the security system should be armed but not monitoring motion for. (i.e. Night)'
  },
  'alarm': {
    'mode': {
      'type': 'mode',
      'context': 'Mode to set home to when alarm is going off. (default: alarm)'
    },
    'lights': {
      'type': 'deviceList',
      'context': 'List of devices to turn on when alarm is triggered.'
    },
    'on_command': {
      'type': 'command',
      'context': 'Command sent to tuen on lights. (default: {"set_light":{"switch":"on","level":100,"ct":6500}} )'
    },
    'alarms': {
      'type': 'deviceList',
      'filter': 'alarm',
      'context': 'List of alarms to turn on when the alarm is triggered.'
    },
    'alarm_command': {
      'type': 'command',
      'context': 'command to send to alarms to set them off. (default: "alarm1" )'
    }
  }
}
