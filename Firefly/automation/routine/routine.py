from Firefly import logging
from Firefly.helpers.automation import Automation
from Firefly.helpers.events import Command, Event
from Firefly.const import SERVICE_NOTIFICATION, COMMAND_NOTIFY

from Firefly.automation.routine.metadata import METADATA, TITLE
from Firefly.automation.routine.const import ROUTINE_ICON, ROUTINE_ROUTINE, ROUTINE_EXECUTE, ROUTINE_MODE
from Firefly.automation.const import AUTOMATION_INTERFACE

# TODO: Routines should take a list of lights to turn off and a list of lights to user definable value.


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine' % package)
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  routine = Routine(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[routine.id] = routine


class Routine(Automation):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, self.event_handler, **kwargs)

    # TODO(zpriddy): Fix this is firebase service
    self._title = TITLE
    self._package = self.package
    self._alias = self.alias


    self.mode = self.interface.get(ROUTINE_MODE, {}).get(ROUTINE_ROUTINE)
    self.icon = self.interface.get(ROUTINE_ICON, {}).get(ROUTINE_ROUTINE, 'new_releases')
    # TODO: replace export_ui with a const from metadata or core.
    self.export_ui = self.interface.get('export_ui', {}).get(ROUTINE_ROUTINE, True)

    self.add_command('execute', self.event_handler)

  def export(self, **kwargs):
    if kwargs.get('firebase_view'):
      return self.get_view(**kwargs)

    export_data = super().export()
    export_data[AUTOMATION_INTERFACE][ROUTINE_ICON] = {ROUTINE_ROUTINE: self.icon}
    # TODO: replace export_ui with a const from metadata or core.
    export_data[AUTOMATION_INTERFACE]['export_ui'] = {ROUTINE_ROUTINE: self.export_ui}
    if self.mode:
      export_data[AUTOMATION_INTERFACE][ROUTINE_MODE] = {ROUTINE_ROUTINE: self.mode}

    return export_data

  def get_view(self, **kwargs):
    view_data = {
      'ff_id': self.id,
      'alias': self.alias,
      'icon':  self.icon,
      'command': 'execute',
      'export_ui': self.export_ui
    }
    return view_data

  def event_handler(self, event: Event = None, trigger_index=0, **kwargs):
    if self.messages.get(ROUTINE_ROUTINE):
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self.messages[ROUTINE_ROUTINE])
      self.firefly.send_command(notify)

    if self.mode:
      self.firefly.location.mode = self.mode

    if self.actions.get(ROUTINE_ROUTINE):
      for a in self.actions[ROUTINE_ROUTINE]:
        a.execute_action(self.firefly)
    return True
