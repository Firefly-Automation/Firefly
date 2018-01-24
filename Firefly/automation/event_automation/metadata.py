AUTHOR = 'Zachary Priddy. (me@zpriddy.com)'
TITLE = 'Event Automation'
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  ['execute'],
  'interface': {
    'trigger_types':    {
      'index_1': {
        'context': 'and / or'
      },
      'index_3': {
        'context': 'and / or'
      },
      'index_2': {
        'context': 'and / or'
      }
    },
    'trigger_devices':  {
      "index_1": {
        'context': 'device_list_1',
        'type':    'deviceList',
        'filter':  {}
      },
      "index_2": {
        'context': 'device_list_2',
        'type':    'deviceList',
        'filter':  {}
      },
      "index_3": {
        'context': 'device_list_2',
        'type':    'deviceList',
        'filter':  {}
      }
    },
    'action_devices':   {
      "index_1": {
        'context': 'device_list_1',
        'type':    'deviceList',
        'filter':  {}
      },
      "index_2": {
        'context': 'device_list_2',
        'type':    'deviceList',
        'filter':  {}
      },
      "index_3": {
        'context': 'device_list_2',
        'type':    'deviceList',
        'filter':  {}
      }
    },
    'trigger_actions':  {
      'index_1': {
        'context': ''
      },
      'index_2': {
        'context': ''
      },
      'index_3': {
        'context': ''
      }
    },
    'commands_actions': {
      'index_1': {
        'context': ''
      },
      'index_2': {
        'context': ''
      },
      'index_3': {
        'context': ''
      }
    },
    'messages':         {
      "index_1": {
        'context': 'Message to send when alert is started.',
        'type':    'string'
      },
      "index_2": {
        'context': 'Message to send when alert is stopped.',
        'type':    'string'
      },
      "index_3": {
        'context': 'Message to send when alert is stopped.',
        'type':    'string'
      }
    },
    'delays':           {
      'index_1': {
        'context': 'Time to delay after door opens before triggering alert. (seconds)',
        'type':    'number'
      },
      'index_2': {
        'context': 'Time to delay after door opens before triggering alert. (seconds)',
        'type':    'number'
      },
      'index_3': {
        'context': 'Time to delay after door opens before triggering alert. (seconds)',
        'type':    'number'
      }
    }
  }
}
