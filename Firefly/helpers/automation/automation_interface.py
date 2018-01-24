# TODO: Build this out as an interface object
from Firefly.helpers.action import Action
from Firefly.automation.triggers import Triggers
from Firefly.helpers.conditions import Conditions

LABEL_ACTIONS = 'actions'
LABEL_CONDITIONS = 'conditions'
LABEL_DELAYS = 'delays'
LABEL_DEVICES = 'devices'
LABEL_MESSAGES = 'messages'
LABEL_TRIGGERS = 'triggers'
LABEL_TRIGGER_ACTION = 'trigger_actions'

INTERFACE_LABELS = [LABEL_ACTIONS, LABEL_CONDITIONS, LABEL_DELAYS, LABEL_DEVICES, LABEL_MESSAGES, LABEL_TRIGGERS, LABEL_TRIGGER_ACTION]


class SubInterface(object):
  def __init__(self, fallback=None):
    self._fallback = fallback

  def add_section(self, section_name, data):
    setattr(self, section_name, data)

  def items(self):
    return_data = self.__dict__.copy()
    return_data.pop('_fallback')
    return return_data.items()

  def export(self):
    return_data = self.__dict__.copy()
    return_data.pop('_fallback')
    return return_data

  def get(self, subsection, fallback='default_fallback'):
    return_value =  self.__getattr__(subsection)
    if return_value == self._fallback and fallback != 'default_fallback':
      return fallback
    return return_value

  def __getitem__(self, item):
    if item in self.__dict__:
      return getattr(self, item)
    return self._fallback

  def __getattr__(self, item):
    if item in self.__dict__:
      return getattr(self, item)
    return self._fallback




class AutomationInterface(object):
  def __init__(self, firefly, ff_id, interface_data):
    self._raw_interface = interface_data
    self._firefly = firefly
    self._id = ff_id

  def export(self):
    export_data = {}
    for index in self.get_indices():
      index_data = self.get_index(index)
      if type(index_data) is SubInterface:
        index_data = index_data.export()
      if index == LABEL_ACTIONS:
        for action_idx, action in index_data.items():
          index_data[action_idx] = [a.export() for a in action]
      if index == LABEL_TRIGGERS:
        for trigger_idx, trigger in index_data.items():
          index_data[trigger_idx] = trigger.export()
      if index == LABEL_CONDITIONS:
        for condition_idx, condition in index_data.items():
          index_data[condition_idx] = condition.export()
      export_data[index] = index_data
    return export_data


  def get_indices(self):
    indices = set(self.__dict__.keys())
    indices.update(INTERFACE_LABELS)
    indices.remove('_id')
    indices.remove('_firefly')
    indices.remove('_raw_interface')
    return indices

  def __getattr__(self, item):
    if item in self.__dict__:
      return getattr(self, item)
    return {}


  def add_index(self, interface_index, fallback=None):
    setattr(self, interface_index, SubInterface(fallback))
    return self.get_index(interface_index)

  def get_index(self, interface_index):
    if interface_index in self.__dict__:
      return getattr(self, interface_index)
    return {}

  def build_interface(self, ignore_setup=False):
    for interface_idx, interface_data in self._raw_interface.items():
      if interface_idx == LABEL_TRIGGER_ACTION:
        self.build_trigger_actions_interface(interface_data)
        continue

      if not ignore_setup:
        if interface_idx == LABEL_ACTIONS:
          self.build_actions_interface(interface_data)
          continue

        if interface_idx == LABEL_CONDITIONS:
          self.build_conditions_interface(interface_data)
          continue

        if interface_idx == LABEL_TRIGGERS:
          self.build_triggers_interface(interface_data)
          continue

      interface_index = self.add_index(interface_idx)
      for sub_idx, data in interface_data.items():
        interface_index.add_section(sub_idx, data)

  def build_trigger_actions_interface(self, interface_data: dict, **kwargs):
    interface_index = self.add_index(LABEL_TRIGGER_ACTION, [])
    for trigger_action_index, trigger_action in interface_data.items():
      interface_index.add_section(trigger_action_index, trigger_action)

  def build_actions_interface(self, interface_data: dict, **kwargs):
    interface_index = self.add_index(LABEL_ACTIONS, [])
    for action_index, action_section in interface_data.items():
      actions_to_add = []
      for action in action_section:
        actions_to_add.append(Action(**action))
      interface_index.add_section(action_index, actions_to_add)

  def build_triggers_interface(self, interface_data: dict, **kwargs):
    interface_index = self.add_index(LABEL_TRIGGERS, [])
    for trigger_idx, trigger_data in interface_data.items():
      trigger_object = Triggers(self._firefly, self._id)
      trigger_object.import_triggers(trigger_data)
      interface_index.add_section(trigger_idx, trigger_object)

  def build_conditions_interface(self, interface_data: dict, **kwargs):
    interface_index = self.add_index(LABEL_CONDITIONS, {})
    for condition_idx, condition_data in interface_data.items():
      if condition_data:
        interface_index.add_section(condition_idx,  Conditions(**condition_data))
