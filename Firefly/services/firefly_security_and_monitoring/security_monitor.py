"""
Firefly Security Monitor

Functions related to doing security monitoring for Firefly.
"""
from Firefly import aliases, logging
from Firefly.const import TYPE_DEVICE
from Firefly.helpers.device import CONTACT, CONTACT_CLOSE, CONTACT_OPEN
from Firefly.helpers.events import Event


def check_all_security_contact_sensors(components, current_state, **kwargs) -> dict:
  contact_states = {
    CONTACT_OPEN:  [],
    CONTACT_CLOSE: []
  }
  logging.info('[FIREFLY SECURITY] checking all contact sensors.')
  for ff_id, component in components.items():
    if component.type == TYPE_DEVICE:
      if component.security and CONTACT in current_state.get(ff_id, {}):
        if current_state[ff_id][CONTACT] == CONTACT_OPEN:
          contact_states[CONTACT_OPEN].append(ff_id)
        else:
          contact_states[CONTACT_CLOSE].append(ff_id)
  return contact_states


def process_contact_change(event: Event, **kwargs) -> dict:
  return_data = {
    'message':       '',
    'contact_event': False,
    'alarm':         False
  }
  if CONTACT not in event.event_action:
    return return_data

  return_data['contact_event'] = True
  alias = aliases.get_alias(event.source)

  if event.event_action[CONTACT] == CONTACT_OPEN:
    return_data['alarm'] = True
    return_data['message'] = 'ALERT! %s has opened while system was armed. Alarm has now been triggered!' % alias
  elif event.event_action[CONTACT] == CONTACT_CLOSE:
    return_data['message'] = 'Warning: System was armed while %s was still opened. %s has been closed. If it opens again before disarming the system the alarm will be triggered.' % (alias, alias)

  return return_data


def generate_contact_warning_message(contact_states: dict, **kwargs):
  message = 'WARNING: There are %s doors/windows left open while arming the alarm system. You may want to check on these to make sure they were not left open by mistake. %s'
  total_open = len(contact_states[CONTACT_OPEN])
  open_devices = []
  for ff_id in contact_states[CONTACT_OPEN]:
    open_devices.append(aliases.get_alias(ff_id))

  return message % (total_open, open_devices)
