from Firefly.const import AUTHOR
from .const import ROUTINE_EXECUTE, ROUTINE_ICON, ROUTINE_MODE, ROUTINE_ROUTINE

# TODO: Make automation const for other const types.

TITLE = 'Firefly Routines'
COMMANDS = [ROUTINE_EXECUTE]
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  COMMANDS,
  'interface': {
    'actions':   {
      ROUTINE_ROUTINE: {
        'context': 'Actions to be executed when routine runs.',
        'type':    'commandList'
      }
    },
    'conditions' : {
      ROUTINE_ROUTINE : {
        'context': 'Conditions that must be met to trigger routine.',
        'type': 'conditions'
      }
    },
    'messages':  {
      ROUTINE_ROUTINE: {
        'context': 'Message to be sent when routine executes.',
        'type':    'string'
      }
    },
    ROUTINE_MODE:      {
      ROUTINE_ROUTINE: {
        'context': 'Mode to be set when routine executes.',
        'type':    'modeString'
      }
    },
    ROUTINE_ICON:      {
      ROUTINE_ROUTINE: {
        'context': 'Name of icon to be displayed on UI.',
        'type':    'iconString'
      }
    },
    'export_ui': {
      ROUTINE_ROUTINE: {
        'context': 'Display routine on web interface.',
        'type':    'boolean'
      }
    },
    'triggers':  {
      ROUTINE_ROUTINE: {
        'context': 'Actions that will trigger the routine',
        'type':    'triggerList'
      }
    },
  }
}