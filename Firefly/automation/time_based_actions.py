from Firefly import logging
from Firefly.automation import Automation
from Firefly.helpers.events import Command
from Firefly.const import AUTHOR

# TODO: move this to automation
from Firefly.util.conditions import check_conditions


TITLE = 'Time Based Actions'
COMMANDS = ['ADD_ACTION']

def Setup(firefly, package, **kwargs):
  """

  Args:
      firefly:
      package:
      kwargs:
  """
  logging.message('Entering %s setup Routine')
  tba = TimeBasedAction(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[tba.id] = tba


class TimeBasedAction(Automation):
  """
  """
  def __init__(self, firefly, package,  **kwargs):
    """

    Args:
        firefly:
        package:
        kwargs:
    """
    super().__init__(firefly, package, TITLE, AUTHOR, self.event_handler, **kwargs)

    self.add_command('ADD_ACTION', self.add_action)
    # actions should be in the form {'command': <COMMAND DICT>, 'conditions': <CONDITIONS DICT>}


  def event_handler(self, event, **kwargs):
    """

    Args:
        event:
        kwargs:

    Returns:

    """
    r = True
    for a in self.actions:
      a.execute_action(self._firefly)
    return r




