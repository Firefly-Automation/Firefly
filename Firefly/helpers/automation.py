from Firefly import aliases
import uuid
from Firefly.automation.triggers import Triggers
from Firefly.helpers.action import Action
from Firefly.helpers.conditions import Conditions

# TODO(zpriddy): These should be in const file
LABEL_TRIGGERS = 'triggers'
LABEL_ACTIONS = 'actions'
LABEL_CONDITIONS = 'conditions'
LABEL_DELAYS = 'delays'
LABEL_MESSAGES = 'messages'
INTERFACE_LABELS = [LABEL_ACTIONS, LABEL_CONDITIONS, LABEL_DELAYS, LABEL_TRIGGERS, LABEL_MESSAGES]

from typing import Callable


class Automation(object):
  def __init__(self, firefly: object, package: str, event_handler: Callable, metadata: dict, interface: dict = {}, **kwargs):
    self.firefly = firefly
    self.metadata = metadata
    self.event_handler = event_handler
    self.interface = interface
    self.actions = {}
    self.triggers = {}
    self.conditions = {}
    self.delays = {}
    self.messages = {}

    # TODO(zpriddy): Should should be a shared function in a lib somewhere.
    # Alias and id functions
    ff_id = metadata.get('ff_id')
    alias = metadata.get('alias')
    # If alias given but no ID look at config files for ID.
    if not ff_id and alias:
      if aliases.get_device_id(alias):
        ff_id = aliases.get_device_id(alias)

    elif ff_id and not alias:
      if aliases.get_alias(ff_id):
        alias = aliases.get_alias(ff_id)

    # If no ff_id ID given -> generate random ID.
    if not ff_id:
      ff_id = str(uuid.uuid4())

    self.id = ff_id
    self.alias = alias if alias else ff_id

  def build_interfaces(self, **kwargs):
    """
    builds the interfaces (actions, conditions, delays, triggers) using the metadata and config information.
    Args:
      **kwargs:

    Returns:

    """
    meta_interfaces = self.metadata.get('interfaces')
    if not meta_interfaces:
      return
    for label in INTERFACE_LABELS:
      interface_data = meta_interfaces.get(label)
      if not interface_data:
        continue
      if label == LABEL_ACTIONS:
        self.build_actions_interface(interface_data)
      if label == LABEL_TRIGGERS:
        self.build_triggers_interface(interface_data)
      if label == LABEL_CONDITIONS:
        self.build_conditions_interface(interface_data)
      if label == LABEL_DELAYS:
        self.build_delays_interface(interface_data)

  def build_actions_interface(self, interface_data: dict, **kwargs):
    for action_index in interface_data.keys():
      self.actions[action_index] = []
      # TODO(zpriddy): Do we want to keep the add_action function?
      for action in self.interface.get(LABEL_ACTIONS).get(action_index):
        self.actions[action_index].append(Action(**action))

  def build_triggers_interface(self, interface_data: dict, **kwargs):
    for trigger_index in interface_data.keys():
      self.triggers[trigger_index] = Triggers(self.firefly, self.id)
      self.triggers[trigger_index].import_triggers(self.interface.get(LABEL_TRIGGERS).get(trigger_index))

  def build_conditions_interface(self, interface_data: dict, **kwargs):
    for condition_index in interface_data.keys():
      self.conditions[condition_index] = []
      for conditions in self.interface.get(LABEL_CONDITIONS).get(condition_index):
        self.conditions[condition_index] = Conditions(**conditions)

  def build_delays_interface(self, interface_data: dict, **kwargs):
    for delay_index in interface_data.keys():
      self.delays[delay_index] = self.interface.get(LABEL_DELAYS).get(delay_index)

  def build_messages_interface(self, interface_data: dict, **kwargs):
    for message_index in interface_data.keys():
      self.messages[message_index] = self.interface.get(LABEL_MESSAGES).get(message_index)
