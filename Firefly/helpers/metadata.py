from Firefly.const import (CONTACT_CLOSED, CONTACT_OPEN, EVENT_ACTION_OFF, EVENT_ACTION_ON, MOTION_ACTIVE, MOTION_INACTIVE, NOT_PRESENT, PRESENT)


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


def metaSwitch(command=True, request=True, primary=False, on_action=EVENT_ACTION_ON, off_action=EVENT_ACTION_OFF, title='switch', context='Change switch.', control_type='select'):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    control_type,
    'options': {
      'on':  on_action,
      'off': off_action
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
      PRESENT:     "Present",
      NOT_PRESENT: "Not Present"
    }
  }
  return meta

def metaQR(command=False, request=False, primary=False, title='qrcode', control_type='qrcode', context='QR Code', data=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    control_type,
    'data': data
  }
  return meta

def metaOwntracks(command=False, request=False, primary=False, title='OwnTracks Config', control_type='otrc', context='Clicks to download owntracks config.', data=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    control_type,
    'data': data
  }
  return meta



def metaText(command=False, request=False, primary=False, title='text', text='', text_request='', context=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type': 'text',
    'options': {
      'text': text,
      'request': text_request
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
      CONTACT_OPEN:   "Open",
      CONTACT_CLOSED: "Closed"
    }
  }
  return meta


def metaMotion(command=False, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'motion',
    'context': 'Motion state of the device.',
    'type':    'text',
    'options': {
      MOTION_ACTIVE:   "Active",
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
      CONTACT_OPEN:   "Empty",
      CONTACT_CLOSED: "Full"
    }
  }
  return meta
