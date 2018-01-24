AUTHOR = 'Zachary Priddy. (me@zpriddy.com)'
TITLE = 'Motion/Door Triggered Lights'
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  ['execute'],
  'interface': {
    'sensors':    {
      'motion': {
        'context': 'motion sensors to use to trigger light',
        'filter':  {
          'motion': True
        },
        'type':    'deviceList'
      },
      'door':   {
        'context': 'door sensors to trigger lights',
        'filter':  {
          'contact': True
        },
        'type':    'deviceList'
      }
    },
    'lights':     {
      "light": {
        'context': 'lights to turn on/off',
        'type':    'deviceList',
        'filter':  {
          'deviceType': ['light', 'switch']
        }
      },
    },
    'commands':   {
      "on":  {
        'context': 'command to send to lights to turn on',
        'type':    'command',
        'filter':  {}
      },
      "off": {
        'context': 'command to send to lights on to turn off',
        'type':    'command',
        'filter':  {}
      }
    },
    'actions':    {
      'on':  {
        'context': 'This is auto generated'
      },
      'off': {
        'context': 'This is auto generated'
      }
    },
    'custom':     {
      'custom_actions': {
        'context': 'set to true if using custom action',
        'type':    'bool'
      }
    },
    'conditions': {
      "on":  {
        'context': 'condition for turning lights on'
      },
      'off': {
        'context': 'condition for turning lights off'
      }
    },
    'delays':     {
      'off': {
        'context': 'Time to delay before turning all lights off (seconds)',
        'type':    'number'
      }
    }
  }
}
