import uuid

from Firefly import aliases, logging
from Firefly.automation.triggers import Triggers
from Firefly.const import TYPE_AUTOMATION, SERVICE_NOTIFICATION, COMMAND_NOTIFY
from Firefly.helpers.action import Action
from Firefly.helpers.conditions import Conditions
from Firefly.helpers.events import Event, Command

# TODO(zpriddy): These should be in const file
LABEL_ACTIONS = 'actions'
LABEL_CONDITIONS = 'conditions'
LABEL_DELAYS = 'delays'
LABEL_MESSAGES = 'messages'
LABEL_TRIGGERS = 'triggers'
INTERFACE_LABELS = [LABEL_ACTIONS, LABEL_CONDITIONS, LABEL_DELAYS, LABEL_MESSAGES, LABEL_TRIGGERS]

from typing import Callable


class Automation(object):
  def __init__(self, firefly, package: str, event_handler: Callable, metadata: dict = {}, interface: dict = {}, **kwargs):
    self.actions = {}
    self.command_map = {}
    self.conditions = {}
    self.delays = {}
    self.event_handler = event_handler
    self.firefly = firefly
    self.interface = interface
    self.messages = {}
    self.metadata = metadata
    self.package = package
    self.triggers = {}

    # TODO(zpriddy): Should should be a shared function in a lib somewhere.
    # Alias and id functions
    ff_id = kwargs.get('ff_id')
    alias = kwargs.get('alias')
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

    self.build_interfaces()

  def event(self, event: Event, **kwargs):
    logging.info('[AUTOMATION] %s - Receiving event: %s' % (self.id, event))
    # Check each triggerList in triggers.
    for trigger_index, trigger in self.triggers.items():
      if trigger.check_triggers(event):
        # Check if there are conditions with the same index, if so check them.
        if self.conditions.get(trigger_index) is not None:
          if not self.conditions[trigger_index].check_conditions(self.firefly):
            continue
        # Call the event handler passing in the trigger_index and return.
        return self.event_handler(event, trigger_index, **kwargs)

  def export(self, **kwargs):
    """
    Export ff_id config with options current values to a dictionary.

    Args:

    Returns:
      (dict): A dict of the ff_id config.
    """
    export_data = {
      'alias':     self.alias,  # 'commands':  self.command_map.keys(),
      'ff_id':     self.id,
      'interface': self.export_interface(),
      'metadata':  self.metadata,
      'package':   self.package,
      'type':      self.type
    }
    return export_data

  def command(self, command, **kwargs):
    """
    Function that is called to send a command to a ff_id.

    Commands can be used to reset times or other items if the automation needs it.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    if command.command in self.command_map.keys():
      try:
        self.command_map[command.command](**command.args)
        return True
      except:
        return False
    return False

  def build_interfaces(self, **kwargs):
    """
    builds the interfaces (actions, conditions, delays, triggers) using the metadata and config information.
    Args:
      **kwargs:

    Returns:

    """
    meta_interfaces = self.metadata.get('interface')
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
      if label == LABEL_MESSAGES:
        self.build_messages_interface(interface_data)

  def build_actions_interface(self, interface_data: dict, **kwargs):
    for action_index in interface_data.keys():
      self.actions[action_index] = []
      # TODO(zpriddy): Do we want to keep the add_action function?
      if not self.interface.get(LABEL_ACTIONS):
        continue
      for action in self.interface.get(LABEL_ACTIONS).get(action_index):
        self.actions[action_index].append(Action(**action))

  def build_triggers_interface(self, interface_data: dict, **kwargs):
    for trigger_index in interface_data.keys():
      if not self.interface.get(LABEL_TRIGGERS):
        continue
      self.triggers[trigger_index] = Triggers(self.firefly, self.id)
      self.triggers[trigger_index].import_triggers(self.interface.get(LABEL_TRIGGERS).get(trigger_index))

  def build_conditions_interface(self, interface_data: dict, **kwargs):
    for condition_index in interface_data.keys():
      self.conditions[condition_index] = None
      if not self.interface.get(LABEL_CONDITIONS):
        continue
      if not self.interface.get(LABEL_CONDITIONS).get(condition_index):
        continue
      self.conditions[condition_index] = Conditions(**self.interface.get(LABEL_CONDITIONS).get(condition_index))

  def build_delays_interface(self, interface_data: dict, **kwargs):
    for delay_index in interface_data.keys():
      if not self.interface.get(LABEL_DELAYS):
        continue
      self.delays[delay_index] = self.interface.get(LABEL_DELAYS).get(delay_index)

  def build_messages_interface(self, interface_data: dict, **kwargs):
    for message_index in interface_data.keys():
      if not self.interface.get(LABEL_MESSAGES):
        continue
      self.messages[message_index] = self.interface.get(LABEL_MESSAGES).get(message_index)

  def export_interface(self, **kwargs):
    interface = {}

    interface[LABEL_TRIGGERS] = {}
    for trigger_index, trigger in self.triggers.items():
      if trigger is None:
        continue
      interface[LABEL_TRIGGERS][trigger_index] = trigger.export()

    interface[LABEL_ACTIONS] = {}
    for action_index, action in self.actions.items():
      interface[LABEL_ACTIONS][action_index] = [a.export() for a in action]

    interface[LABEL_CONDITIONS] = {}
    for condition_index, condition in self.conditions.items():
      if condition is None:
        continue
      interface[LABEL_CONDITIONS][condition_index] = condition.export()

    interface[LABEL_MESSAGES] = {}
    for message_index, message in self.messages.items():
      if message is None:
        continue
      interface[LABEL_MESSAGES][message_index] = message

    interface[LABEL_DELAYS] = {}
    for delay_index, delay in self.delays.items():
      if delay is None:
        continue
      interface[LABEL_DELAYS][delay_index] = delay

    return interface

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self.command_map[command] = function

  def execute_actions(self, action_index: str, **kwargs) -> bool:
    if not self.actions.get(action_index):
      return False
    for action in self.actions.get(action_index):
      action.execute_action(self.firefly)
    return True

  def send_messages(self, message_index: str, **kwargs) -> bool:
    if not self.messages.get(message_index):
      return False
    notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self.messages.get(message_index))
    self.firefly.send_command(notify)
    return True

  @property
  def type(self):
    return TYPE_AUTOMATION
