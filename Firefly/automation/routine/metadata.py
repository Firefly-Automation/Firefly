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
    'lights':          {
      'off':       {
        'context': 'Turn off these lights when the routine executes.',
        'type':    'deviceList'
      },
      'off_night': {
        'context': 'Turn off these lights when the routine executes after sunset.',
        'type':    'deviceList'
      },
      'off_day':   {
        'context': 'Turn off these lights when the routine executes before sunset.',
        'type':    'deviceList'
      },
      'on':        {
        'context': 'Turn on these lights when the routine executes.',
        'type':    'deviceList'
      },
      'on_night':  {
        'context': 'Turn on these lights when the routine executes after sunset.',
        'type':    'deviceList'
      },
      'on_day':    {
        'context': 'Turn on these lights when the routine executes before sunset.',
        'type':    'deviceList'
      }
    },
    'commands':        {
      'off':       {
        'context': 'command to send to lights when turning them off. Defaults to {set_light:{switch:off}}',
        'type':    'command'
      },
      'off_night': {
        'context': 'command to send to lights when turning them off after sunset. Defaults to {set_light:{switch:off}}',
        'type':    'command'
      },
      'off_day':   {
        'context': 'command to send to lights when turning them off before sunset. Defaults to {set_light:{switch:off}}',
        'type':    'command'
      },
      'on':        {
        'context': 'command to send to lights when turning them on. Defaults to {set_light:{switch:on}}',
        'type':    'command'
      },
      'on_day':    {
        'context': 'command to send to lights when turning them on before sunset. Defaults to {set_light:{switch:on}}, you could do {set_light:{switch:on,ct:6500}}',
        'type':    'command'
      },
      'on_night':  {
        'context': 'command to send to lights when turning them on after sunset. Defaults to {set_light:{switch:on}}, you could do {set_light:{switch:on,ct:2700}}',
        'type':    'command'
      }
    },
    'actions':         {
      ROUTINE_ROUTINE: {
        'context': 'Actions to be executed when routine runs.',
        'type':    'commandList'
      }
    },
    'conditions':      {
      ROUTINE_ROUTINE: {
        'context': 'Conditions that must be met to trigger routine.',
        'type':    'conditions'
      }
    },
    'auto_transition': {
      'sunrise': {
        'context': 'Auto change lights and switches when the sun raises. (defaults true)',
        'type':    'bool'
      },
      'sunset': {
        'context': 'Auto change lights and switches when the sun sets. (defaults true)',
        'type':    'bool'
      }
    },
    'messages':        {
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
    'export_ui':       {
      ROUTINE_ROUTINE: {
        'context': 'Display routine on web interface.',
        'type':    'boolean'
      }
    },
    'triggers':        {
      ROUTINE_ROUTINE: {
        'context': 'Actions that will trigger the routine',
        'type':    'triggerList'
      }
    },
  }
}
