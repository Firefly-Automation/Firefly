from Firefly.helpers.device import CONTACT, CONTACT_CLOSE, CONTACT_OPEN

LOW_BATTERY_PERCENT = 'low_battery_percent'
CRITICAL_BATTERY_PERCENT = 'critical_battery_percent'
BATTERY_LOW = 'battery_low'
BATTERY_CRITICAL = 'battery_critical'
BATTERY_OKAY = 'battery_okay'
BATTERY_NOT_REPORTED = 'battery_not_reported'
ALARM_ARMED_MESSAGE_NO_MOTION = 'Alarm system is now armed without motion active'
ALARM_ARMED_MESSAGE_MOTION = 'Alarm system is now armed with motion active'

BATTERY_NO_NOTIFY_STATES = [BATTERY_OKAY, BATTERY_NOT_REPORTED]
BATTERY_NOTIFY_STATES = [BATTERY_LOW, BATTERY_CRITICAL]

STATUS_TEMPLATE = {
  CONTACT: {
    'status': 'okay',
    'message': '',
    CONTACT_OPEN:  {
      'count':   0,
      'devices': []
    },
    CONTACT_CLOSE: {
      'count':   0,
      'devices': []
    }
  }
}
