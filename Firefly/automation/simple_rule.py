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
    'actions':    {
      "initial": {
        'context': 'Actions to be executed when on initial trigger.',
        'type':    'commandList'
      },
      "delayed": {
        'context': 'Actions to be executed when on delayed trigger.',
        'type':    'commandList'
      }
    },
    'messages':   {
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
    'triggers':   {
      "initial": {
        'context': 'Triggers to initially trigger the initial actions.',
        'type':    'triggerList'
      },
      "delayed": {
        'context': 'Triggers to trigger the delayed actions.',
        'type':    'triggerList'
      }
    },
    'delays':     {
      'delayed': {
        'context': 'Time to delay after delayed trigger is triggered before executing actions. (seconds)',
        'type':    'number'
      },
      'initial': {
        'context': 'Time to delay before initial actions are executed. (seconds)',
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
  simeple_rule = SimpleRule(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[simeple_rule.id] = simeple_rule


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

  def initial_event_handler(self, event: Event = None, trigger_index="initial", skip_delay=False, **kwargs):
    """ Handle the initial event trigger.
    Args:
      event: (Event) The event that triggered the handler.
      trigger_index: (str) Trigger index (key) in the metadata.
      skip_delay: (bool) Skip the initial delay. This is used in case there is an initial delay, the delayed function will call this function and tell it to skip the initial delay.
      **kwargs:
    """
    # If it's the first time getting triggered then send the message.
    # If it has already been triggered then cancel the current delayed action timer.
    if not skip_delay and not self.triggered and self.delays.get(trigger_index):
      scheduler.runInS(self.delays.get(trigger_index), self.initial_event_handler, self.timer_id, True, event=event, trigger_index=trigger_index, skip_delay=True)
      return
    if not self.triggered:
      self.send_messages(trigger_index)
      self.triggered = True
    else:
      scheduler.cancel(self.timer_id)
    self.execute_actions(trigger_index)

  def delayed_event_handler(self, event: Event = None, trigger_index="delayed", **kwargs):
    # If it has not been triggered then stop.
    if not self.triggered:
      # Cancel timer if it's currently waiting for initial delay.
      scheduler.cancel(self.timer_id)
      return
    # If there is a delay, wait for the delay and then execute, otherwise execute.
    if self.delays.get(trigger_index):
      scheduler.runInS(self.delays.get(trigger_index), self.execute_delayed_actions, self.timer_id, True, trigger_index=trigger_index)
    else:
      self.execute_delayed_actions(trigger_index)

  def execute_delayed_actions(self, trigger_index="delayed", **kwargs):
    self.triggered = False
    self.send_messages(trigger_index)
    self.execute_actions(trigger_index)
