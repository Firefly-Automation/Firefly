from Firefly.const import (CONTACT_CLOSED, CONTACT_OPEN, EVENT_ACTION_OFF, EVENT_ACTION_ON, MOTION_ACTIVE,
                           MOTION_INACTIVE, NOT_PRESENT, PRESENT)

def metaDimmer(min=0, max=100, command=True, request=False, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'dimmer',
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
    'title':   'switch',
    'context': 'Change switch.',
    'type':    'select',
    'options': {
      EVENT_ACTION_ON: "On",
      EVENT_ACTION_OFF: "Off"
    }
  }
  return meta


def metaPresence(command=True, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'presence',
    'context': 'Set the presence of a device.',
    'type':    'select',
    'options': {
      PRESENT: "Present",
      NOT_PRESENT: "Not Present"
    }
  }
  return meta


def metaContact(command=False, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'contact',
    'context': 'Contact state of the device.',
    'type':    'text',
    'options': {
      CONTACT_OPEN: "Open",
      CONTACT_CLOSED: "Closed"
    }
  }
  return meta


def metaMotion(command=False, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title': 'motion',
    'context': 'Motion state of the device.',
    'type':    'text',
    'options': {
      MOTION_ACTIVE: "Active",
      MOTION_INACTIVE: "Inactive"
    }
  }
  return meta

def metaWaterLevel(command=False, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'water_level',
    'context': 'Is it full or empty',
    'type':    'text',
    'options': {
      CONTACT_OPEN: "Empty",
      CONTACT_CLOSED: "Full"
    }
  }
  return meta
