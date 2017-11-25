"""
Battery monitoring functions for Firefly Security and Monitoring
"""
from Firefly.helpers.events import Event
from Firefly import logging, aliases
from Firefly.helpers.device import BATTERY
from .const import LOW_BATTERY_PERCENT, CRITICAL_BATTERY_PERCENT, BATTERY_LOW, BATTERY_CRITICAL, BATTERY_OKAY, BATTERY_NOT_REPORTED

SETTINGS = {
  LOW_BATTERY_PERCENT:      70,
  CRITICAL_BATTERY_PERCENT: 5
}

MESSAGES = {
  BATTERY_LOW: '%s has a low battery. Please look into replacing the battery soon.',
  BATTERY_CRITICAL: '%s has a critically low battery. This battery needs to get replaced ASAP. You will keep recieving these notifications until the battery is replaced.'
}

def check_battery_from_event(event: Event, **kwargs):
  battery_level = event.event_action.get(BATTERY)

  #TODO: Fix this using const
  if battery_level == 'NOT REPORTED':
    return BATTERY_NOT_REPORTED

  if battery_level is None:
    logging.warn('[BATTERY MONITOR] battery not in event')
    return BATTERY_NOT_REPORTED

  try:
    battery_level = int(battery_level)
    if battery_level <= SETTINGS[CRITICAL_BATTERY_PERCENT]:
      return BATTERY_CRITICAL
    if battery_level <= SETTINGS[LOW_BATTERY_PERCENT]:
      return BATTERY_LOW
    return BATTERY_OKAY
  except Exception as e:
    logging.warn('[BATTERY MONITOR] battery level not reported as numeric value. ff_id:%s - battery_level: %s - error: %s' % (event.source, battery_level, e))
    return BATTERY_NOT_REPORTED

def generate_battery_notification_message(ff_id, battery_state, **kwargs):
  alias = aliases.get_alias(ff_id)
  return MESSAGES[battery_state] % alias
