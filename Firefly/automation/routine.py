# TODO: The base of this should become package automation
import asyncio

from Firefly import logging
from Firefly.automation import Triggers, Trigger, Automation
from Firefly.helpers.events import Command

# TODO: move this to automation
from Firefly.util.conditions import check_conditions


AUTHOR = 'Zachary Priddy me@zpriddy.com'
TITLE = 'Firefly Routines'
COMMANDS = ['ADD_ACTION']

def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine')
  routine = Routine(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[routine.id] = routine


class Routine(Automation):
  def __init__(self, firefly, package,  **kwargs):
    super().__init__(firefly, package, TITLE, AUTHOR, self.event_handler, **kwargs)

    self.add_command('ADD_ACTION', self.add_action)
    # actions should be in the form {'command': <COMMAND DICT>, 'conditions': <CONDITIONS DICT>}
    self._actions = kwargs.get('actions') if kwargs.get('actions') else []


  def add_action(self, command, **kwargs):
    action_command = kwargs.get('actions_command')
    action_conditions = kwargs.get('action_conditions')
    if not action_command or not action_conditions:
      return False

    self._actions.append({'command':action_command, 'conditions': action_conditions})
    return True

  def export(self, **kwargs):
    export_data =  super().export(**kwargs)
    export_data['actions'] = self._actions
    return export_data


  def event_handler(self, event, **kwargs):
    print('************************* ROUTINE ***************************************')
    r = True
    for a in self._actions:
      command = Command(**a.get('command'))
      conditions = a.get('conditions')
      if check_conditions(self._firefly, conditions):
        r &= yield from self._firefly.send_command(command)
    print(r)
    return r




