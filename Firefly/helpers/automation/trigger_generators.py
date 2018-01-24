"""
Functions for generating triggers from lists of devices.

"""
from typing import TypeVar

from Firefly.helpers.device import CONTACT, CONTACT_CLOSE, CONTACT_OPEN, MOTION, MOTION_ACTIVE, MOTION_INACTIVE, PRESENCE, PRESENT, NOT_PRESENT

TRIGGER_ACTION = TypeVar('TRIGGER_ACTION', dict, str)


def generate_and_trigger(trigger_action: TRIGGER_ACTION, device_list: list) -> list:
  """Generates an AND trigger list that can be imported into an interface for automation actions.

  Example:
    # Trigger when all windows are opened
    windows = interface['devices']['windows']
    trigger_action = {CONTACT: CONTACT_OPEN}
    window_triggers = generate_and_trigger(trigger_action, windows)
    interface['triggers']['initial'] = window_triggers

  Args:
    trigger_action: the trigger action as a dict or list
      example: {CONTACT:CONTACT_CLOSED} or [{CONTACT:CONTACT_CLOSED},{ALARM:3}]
    device_list: the list of ff_id's to generate actions for

  Returns: List of triggers to import at the beginning of automation.
  """
  trigger_list = []
  if type(trigger_action) is dict:
    trigger_action = [trigger_action]

  for device in device_list:
    trigger_list.append({
      'listen_id':      device,
      'source':         'SOURCE_TRIGGER',
      'trigger_action': trigger_action
    })

  return [trigger_list]


def generate_or_trigger(trigger_action: TRIGGER_ACTION, device_list: list) -> list:
  """Generates an OR trigger list that can be imported into an interface for automation actions.

  Example:
    # Trigger when one of the  windows are opened
    windows = interface['devices']['windows']
    trigger_action = {CONTACT: CONTACT_OPEN}
    window_triggers = generate_or_trigger(trigger_action, windows)
    interface['triggers']['initial'] = window_triggers

  Args:
    trigger_action: the trigger action as a dict or list
      example: {CONTACT:CONTACT_CLOSED} or [{CONTACT:CONTACT_CLOSED},{ALARM:3}]
    device_list: the list of ff_id's to generate actions for

  Returns: List of triggers to import at the beginning of automation.
  """
  trigger_list = []
  if type(trigger_action) is dict:
    trigger_action = [trigger_action]

  for device in device_list:
    trigger_list.append([{
      'listen_id':      device,
      'source':         'SOURCE_TRIGGER',
      'trigger_action': trigger_action
    }])

  return trigger_list


TRIGGER_CONTACT_OPEN = {
  CONTACT: [CONTACT_OPEN]
}
TRIGGER_CONTACT_CLOSE = {
  CONTACT: [CONTACT_CLOSE]
}
TRIGGER_MOTION_ACTIVE = {
  MOTION: [MOTION_ACTIVE]
}
TRIGGER_MOTION_INACTIVE = {
  MOTION: [MOTION_INACTIVE]
}
TRIGGER_PRESENT = {
  PRESENCE : [PRESENT]
}
TRIGGER_NOT_PRESENT = {
  PRESENCE: [NOT_PRESENT]
}


def generate_contact_open_trigger(device_list: list, logic_or=True) -> list:
  """ Generate OR triggerList that will trigger when contact sensor opened.

  Args:
    device_list: List of contact sensors
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_CONTACT_OPEN, device_list)
  return generate_and_trigger(TRIGGER_CONTACT_OPEN, device_list)


def generate_contact_close_trigger(device_list: list, logic_or=False) -> list:
  """ Generate OR triggerList that will trigger when contact sensor closed.

  Args:
    device_list: List of contact sensors
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_CONTACT_CLOSE, device_list)
  return generate_and_trigger(TRIGGER_CONTACT_CLOSE, device_list)


def generate_motion_active_trigger(device_list: list, logic_or=True) -> list:
  """ Generate OR triggerList that will trigger when motion sensor is active.

  Args:
    device_list: List of motion sensors
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_MOTION_ACTIVE, device_list)
  return generate_and_trigger(TRIGGER_MOTION_ACTIVE, device_list)


def generate_motion_inactive_trigger(device_list: list, logic_or=False) -> list:
  """ Generate OR triggerList that will trigger when motion sensor is inactive.

  Args:
    device_list: List of motion sensors
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_MOTION_INACTIVE, device_list)
  return generate_and_trigger(TRIGGER_MOTION_INACTIVE, device_list)

def generate_present_trigger(device_list: list, logic_or=True) -> list:
  """ Generate OR triggerList that will trigger when presence devices are present.

  Args:
    device_list: List of presence devices
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_PRESENT, device_list)
  return generate_and_trigger(TRIGGER_PRESENT, device_list)


def generate_not_present_trigger(device_list: list, logic_or=False) -> list:
  """ Generate OR triggerList that will trigger when presence devices are not present.

  Args:
    device_list: List of presence devices
    logic_or: Use the OR logic, if set to False use AND logic
  """
  if logic_or:
    return generate_or_trigger(TRIGGER_NOT_PRESENT, device_list)
  return generate_and_trigger(TRIGGER_NOT_PRESENT, device_list)
