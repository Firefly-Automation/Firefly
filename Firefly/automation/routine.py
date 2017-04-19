from Firefly import logging
from Firefly.automation import Automation
from Firefly.helpers.events import Command
from Firefly.const import SERVICE_NOTIFICATION, COMMAND_NOTIFY, AUTHOR

TITLE = 'Firefly Routines'
COMMANDS = ['add_action', 'execute']


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine')
  routine = Routine(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[routine.id] = routine


class Routine(Automation):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, self.event_handler, **kwargs)

    self.add_command('add_action', self.add_action)
    self.add_command('execute', self.event_handler)
    self._message = kwargs.get('message')
    self._set_mode = kwargs.get('mode')

  def export(self, **kwargs):
    export_data = super().export()
    if self._message:
      export_data['message'] = self._message
    if self._set_mode:
      export_data['mode'] = self._set_mode
    return export_data

  def event_handler(self, event=None, **kwargs):
    if self._message:
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self._message)
      self._firefly.send_command(notify)

    if self._set_mode:
      self._firefly.location.mode = self._set_mode

    for a in self.actions:
      a.execute_action(self._firefly)
    return True

