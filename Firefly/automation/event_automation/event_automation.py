from .metadata import METADATA, AUTHOR, TITLE
from Firefly import logging, scheduler
from Firefly.helpers.automation import Automation
from Firefly.helpers.automation.automation_interface import AutomationInterface
from Firefly.helpers.automation.trigger_generators import generate_and_trigger, generate_or_trigger
from uuid import uuid4
from Firefly.helpers.events import Event, Request, Command

# TODO(zpriddy): These should be in const file
LABEL_TRIGGERS = 'triggers'

def Setup(firefly, package, **kwargs):
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  else:
    kwargs['metadata'].update(METADATA)
  event_automation = EventAction(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[event_automation.id] = event_automation


class EventAction(Automation):
  def __init__(self, firefly, package, **kwargs):
    interface_data = kwargs.get('interface', {})
    interface = AutomationInterface(firefly, 'not_set', interface_data)
    interface.build_interface(ignore_setup=True)

    index_list = ['index_1', 'index_2']
    interface_data['triggers'] = {}
    trigger_actions = []
    for index in index_list:
      if interface.trigger_types.get(index) == 'and':
        trigger_actions = generate_and_trigger(interface.trigger_actions.get(index), interface.trigger_devices.get(index))
      elif interface.trigger_types.get(index) == 'or':
        trigger_actions = generate_or_trigger(interface.trigger_actions.get(index), interface.trigger_devices.get(index))
      interface_data['triggers'][index] = trigger_actions

    kwargs['interface'] = interface_data


    super().__init__(firefly, package, self.event_handler, **kwargs)



  def event_handler(self, event: Event = None, trigger_index="", **kwargs):
    logging.info('[EVENT ACTIONS] EVENT HANDLER: %s' % trigger_index)

    self.execute_actions(trigger_index)