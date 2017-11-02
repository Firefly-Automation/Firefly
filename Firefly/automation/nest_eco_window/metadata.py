AUTHOR = 'Zachary Priddy. (me@zpriddy.com)'
TITLE = 'Nest Eco Window'
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  [],
  'interface': {
    'devices':    {
      "windows": {
        'context': 'Windows that will trigger this automation.',
        'type':    'deviceList',
        'filter': {
          'request': ['contact']
        }
      },
    },
    'send_messages':   {
      "send": {
        'context': 'Send message when chaning the mode of the Nest.',
        'type':    'boolean'
      }
    },
    'delays':     {
      'delayed': {
        'context': 'Time to delay after window closes before changing Nest mode. (seconds)',
        'type':    'number'
      },
      'initial': {
        'context': 'Time to delay after window opens before changing Nest mode. (seconds)',
        'type':    'number'
      }
    }
  }
}