AUTHOR = 'Zachary Priddy. (me@zpriddy.com)'
TITLE = 'Door Alert'
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  ['start', 'stop'],
  'interface': {
    'devices':  {
      "contact_sensors": {
        'context': 'Doors/Windows that will trigger the alert.',
        'type':    'deviceList',
        'filter':  {
          'request': ['contact']
        }
      },
      "lights":          {
        'context': 'Lights that will flash.',
        'type':    'deviceList',
        'filter':  {
          'request': ['light']
        }
      }
    },
    'triggers': {
      'initial': {
        'context': 'THIS IS AUTO GENERATED'
      },
      'delayed': {
        'context': 'THIS IS AUTO GENERATED'
      }
    },
    'messages':  {
      "initial": {
        'context': 'Message to send when alert is started.',
        'type':    'string'
      },
      "delayed": {
        'context': 'Message to send when alert is stopped.',
        'type':    'string'
      }
    },
    'delays':   {
      'initial': {
        'context': 'Time to delay after door opens before triggering alert. (seconds)',
        'type':    'number'
      }
    }
  }
}
