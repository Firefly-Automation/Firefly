from Firefly.const import (EVENT_ACTION_ON, EVENT_ACTION_OFF, PRESENT, NOT_PRESENT)


def metaDimmer(min=0, max=100, command=True, request=False, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'context': 'Change dimmer level.',
    'type':    'number',
    'options': {
      'min': min,
      'max': max
    }
  }
  return meta


def metaSwitch(command=True, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'context': 'Change dimmer level.',
    'type':    'select',
    'options': {
      "On":  EVENT_ACTION_ON,
      "Off": EVENT_ACTION_OFF
    }
  }
  return meta

def metaPresence(command=True, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'context': 'Set the presence of a device.',
    'type':    'select',
    'options': {
      "Present":  PRESENT,
      "Not Present": NOT_PRESENT
    }
  }
  return meta