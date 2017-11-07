AUTHOR = 'Zachary Priddy. (me@zpriddy.com)'
TITLE = 'Window Fan Controls'
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  ['execute'],
  'interface': {
    'sensors':     {
      'temperature': {
        'context': 'temperature sensors to use to check the temperature inside',
        'filter':  {
          'temperature': True
        },
        'type':    'deviceList'
      },
      'windows':      {
        'context': 'window sensors to check to make sure windows are open',
        'filter':  {
          'contact': True
        },
        'type':    'deviceList'
      }
    },
    'switches':    {
      "fans": {
        'context': 'control these fans',
        'type':    'deviceList',
        'filter':  {
          'deviceType': ['fan', 'switch']
        }
      },
    },
    'temperature': {
      "high":  {
        'context': 'turn on the fans if the temperature goes past',
        'type':    'number',
        'filter':  {}
      },
      "low": {
        'context': 'turn off the fans if the temperature goes past',
        'type':    'number',
        'filter':  {}
      },
    },
    'actions':     {
      'on':  {
        'context': 'This is auto generated'
      },
      'off': {
        'context': 'This is auto generated'
      }
    },
    'conditions':  {
      "on":  {
        'context': 'condition for turning lights on'
      },
      'off': {
        'context': 'condition for turning lights off'
      }
    },
    'delays':      {
      'off': {
        'context': 'Time to delay before turning off the fan(seconds)',
        'type':    'number'
      },
      'on':  {
        'context': 'Time to delay before turning on the fans (seconds)',
        'type':    'number'
      }
    }
  }
}
