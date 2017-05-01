from Firefly import logging
from Firefly.automation import Automation
from Firefly.helpers.events import Command
from Firefly.const import SERVICE_NOTIFICATION, COMMAND_NOTIFY, AUTHOR, CONTACT_CLOSED, CONTACT_OPEN, SWITCH_ON, SWITCH_OFF
from Firefly.automation.triggers import Triggers
from Firefly.helpers.conditions import Conditions
from Firefly.helpers.action import Action
import uuid
from Firefly import scheduler

INVERSE_MAPPING={
  SWITCH_ON: SWITCH_OFF,
  SWITCH_OFF: SWITCH_ON,
  CONTACT_OPEN: CONTACT_CLOSED,
  CONTACT_CLOSED: CONTACT_OPEN
}


TITLE = 'Firefly Event Based Action'
COMMANDS = ['add_action', 'execute']


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine')
  event_action = EventAction(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[event_action.id] = event_action


class EventAction(Automation):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, self.event_handler, **kwargs)

    self.add_command('add_action', self.add_action)
    self.add_command('execute', self.event_handler)
    self._message = kwargs.get('message')
    self._delay_s = kwargs.get('delay_s')
    self._delay_m = kwargs.get('delay_m')
    self._delay_h = kwargs.get('delay_h')

    # _initial_trigger will be used to know when to only check delayed triggers
    self._initial_triggered = False
    self._has_delayed_triggers = False

    # Auto Inverse will auto-generate the reverse actions
    # TODO: For now this is not enabled
    self._auto_inverse = False
    self._delayed_actions = []

    self._action_id = str(uuid.uuid4())

    if not self._auto_inverse:
      self._delayed_triggers = Triggers(firefly, self.id)

      triggers = kwargs.get('delayed_triggers')
      if triggers:
        self.import_delayed_triggers(triggers)

      if kwargs.get('use_same_conditions'):
        conditions = kwargs.get('conditions')
      else:
        conditions = kwargs.get('delayed_conditions')
      if conditions:
        self._delayed_conditions = Conditions(**conditions)
      else:
        self._delayed_conditions = None

      actions = kwargs.get('delayed_actions')
      if actions:
        for action in actions:
          self._delayed_actions.append(Action(**action))

    else:
      logging.warn("Inverse Actions not supported yet.")

    self._has_delayed_triggers = True if len(self._delayed_triggers.triggers) > 0 else False


  def import_delayed_triggers(self, triggers):
    logging.info('Importing delayed triggers into %s - %s' % (self.id, triggers))
    self._delayed_triggers.import_triggers(triggers)

  def export(self, **kwargs):
    export_data = super().export()
    export_data['delayed_action'] = self.delayed_actions_export
    export_data['delayed_triggers'] = self.delayed_triggers.export()
    if self._delay_s:
      export_data['delay_s'] = self._delay_s
    if self._delay_m:
      export_data['delay_m'] = self._delay_m
    if self._delay_h:
      export_data['delay_h'] = self._delay_h
    return export_data

  @property
  def delayed_actions_export(self):
    exported_actions = []
    for act in self._delayed_actions:
      print(act)
      print(type(act))
      exported_actions.append(act.export())
    return exported_actions

  @property
  def delayed_triggers(self):
    return self._delayed_triggers


  def event(self, event, **kwargs):
    logging.info('[AUTOMATION] %s - Receiving event: %s' % (self.id, event))

    if not self._has_delayed_triggers or (self._has_delayed_triggers and not self._initial_triggered):
      valid = True
      if self.conditions:
        valid &= self.conditions.check_conditions(self._firefly)
      valid &= self.triggers.check_triggers(event)
      if valid:
        #self.get_event_handler(event, **kwargs)
        self.event_handler(event, **kwargs)

    elif self._has_delayed_triggers and self._initial_triggered:
      valid = True
      if self.conditions:
        valid &= self.conditions.check_conditions(self._firefly)
      valid &= self.triggers.check_triggers(event)
      if valid:
        scheduler.cancel(self._action_id)


    if self._initial_triggered:
      # TODO handel delayed conditions
      valid = True
      valid &= self.delayed_triggers.check_triggers(event)
      if valid:
        if self._delay_s:
          scheduler.runInS(self._delay_s, self.delayed_event_handler, job_id=self._action_id)
        elif self._delay_m:
          scheduler.runInM(self._delay_m, self.delayed_event_handler, job_id=self._action_id)
        elif self._delay_h:
          scheduler.runInH(self._delay_h, self.delayed_event_handler, job_id=self._action_id)
        else:
          self.delayed_event_handler(event, **kwargs)

    # TODO: Handel delay triggers
    # The logic here should be something along the line of if there is a flag of wait_delay_trigger then set a flag of
    # triggered=true, if triggered is true then we are only going to check conditions for delayed triggers, otherwise
    # check triggers for both. If delayed check are true then do delayed actions. For now I am going to focus on time
    # delayed reverse actions.
    #
    # It would be nice for triggers to have a trigger ID to report what trigger caused this to trigger. However this may
    # create other problems with triggers. So this idea may need to be scrapped.

  def event_handler(self, event=None, **kwargs):
    if self._message:
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self._message)
      self._firefly.send_command(notify)

    for a in self.actions:
      a.execute_action(self._firefly)

    self._initial_triggered = True
    scheduler.cancel(self._action_id)

    if not self._has_delayed_triggers:
      if self._delay_s:
        scheduler.runInS(self._delay_s, self.delayed_event_handler, job_id=self._action_id)
      if self._delay_m:
        scheduler.runInM(self._delay_m, self.delayed_event_handler, job_id=self._action_id)
      if self._delay_h:
        scheduler.runInH(self._delay_h, self.delayed_event_handler, job_id=self._action_id)

    # TODO: Handel delay triggers
    return True


  def delayed_event_handler(self, event=None, **kwargs):
    self._initial_triggered = False

    if self._message:
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self._message)
      self._firefly.send_command(notify)

    valid = True
    if self._delayed_conditions:
      valid &= self.conditions.check_conditions(self._firefly)
      # TODO: Handel delay triggers

    if not valid:
      return False

    for a in self.delayed_actions:
      a.execute_action(self._firefly)
    return True

  @property
  def delayed_actions(self):
    return self._delayed_actions