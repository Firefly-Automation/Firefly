from uuid import uuid4

from Firefly import logging, scheduler
from Firefly.const import AUTHOR
from Firefly.helpers.automation import Automation
from Firefly.helpers.events import Event

TITLE = 'Firefly Simple Rule'
COMMANDS = ['execute']
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  COMMANDS,
  'interface': {
    'actions':  {
      "initial": {
        'context': 'Actions to be executed when on initial trigger.',
        'type':    'commandList'
      },
      "delayed": {
        'context': 'Actions to be executed when on delayed trigger.',
        'type':    'commandList'
      }
    },
    'messages': {
      "initial": {
        'context': 'Message to be sent on initial trigger.',
        'type':    'string'
      },
      "delayed": {
        'context': 'Message to be sent on delayed trigger.',
        'type':    'string'
      }
    },
    'conditions': {
      "initial": {
        'context': 'Condition for initial trigger.',
        'type':    'condition'
      },
      "delayed": {
        'context': 'Condition for delayed trigger.',
        'type':    'condition'
      }
    },
    'triggers': {
      "initial": {
        'context': 'Triggers to initially trigger the initial actions.',
        'type':    'triggerList'
      },
      "delayed": {
        'context': 'Triggers to trigger the delayed actions.',
        'type':    'triggerList'
      }
    },
    'delays':   {
      'delay': {
        'context': 'Time to delay after delayed trigger is triggered before executing actions. (seconds)',
        'type':    'number'
      }
    }
  }
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup simple_rules' % package)
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  else:
    kwargs['metadata'].update(METADATA)
  simepl_rule = SimpleRule(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[simepl_rule.id] = simepl_rule


class SimpleRule(Automation):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, self.event_handler, **kwargs)
    self.triggered = False
    self.timer_id = str(uuid4())

    # TODO(zpriddy): Fix this is firebase service
    self._title = TITLE
    self._package = self.package
    self._alias = self.alias

  def event_handler(self, event: Event = None, trigger_index="", **kwargs):
    if trigger_index == "initial":
      self.initial_event_handler(event, trigger_index)
    if trigger_index == "delayed":
      self.delayed_event_handler(event, trigger_index)

  def initial_event_handler(self, event: Event = None, trigger_index="initial", **kwargs):
    # If it's the first time getting triggered then send the message.
    # If it has already been triggered then cancel the current delayed action timer.
    if not self.triggered:
      self.send_messages(trigger_index)
      self.triggered = True
    else:
      scheduler.cancel(self.timer_id)
    self.execute_actions(trigger_index)

  def delayed_event_handler(self, event: Event = None, trigger_index="delayed", **kwargs):
    # If it has not been triggered then stop.
    if not self.triggered:
      return
    # If there is a delay, wait for the delay and then execute, otherwise execute.
    if self.delays.get('delay'):
      scheduler.runInS(self.delays.get('delay'), self.execute_delayed_actions, self.timer_id, True, trigger_index=trigger_index)
    else:
      self.execute_delayed_actions(trigger_index)

  def execute_delayed_actions(self, trigger_index="delayed", **kwargs):
    self.triggered = False
    self.send_messages(trigger_index)
    self.execute_actions(trigger_index)

