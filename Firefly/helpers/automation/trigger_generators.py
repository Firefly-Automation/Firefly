"""
Functions for generating triggers from lists of devices.

"""
from typing import TypeVar

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
      'listen_id': device,
      'source': 'SOURCE_TRIGGER',
      'trigger_action' : trigger_action
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