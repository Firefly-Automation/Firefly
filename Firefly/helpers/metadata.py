from Firefly.const import (CONTACT_CLOSED, CONTACT_OPEN, EVENT_ACTION_OFF, EVENT_ACTION_ON, MOTION_ACTIVE, MOTION_INACTIVE, NOT_PRESENT, PRESENT, CONTACT)


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


def metaSlider(command=True, request=False, primary=False, min=0, max=100, step=1, action_type='slider', request_param='level', context='Change slider.', title='slider', set_command='',
               command_param=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    action_type,
    'options': {
      'min':           min,
      'max':           max,
      'step':          step,
      'request':       request_param,
      'command':       set_command,
      'command_param': command_param,
    }
  }
  return meta


def metaButton(command=True, request=False, primary=False, action_type='button', text='Button', context='Button', title='Button', set_command='', command_param='', command_value=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    action_type,
    'options': {
      'text':          text,
      'command':       set_command,
      'command_param': command_param,
      'command_value': command_value
    }
  }
  return meta


def metaButtons(command=False, request=False, primary=False, action_type='buttons', context='Button', title='Buttons', buttons=[], request_val=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    action_type,
    'options': {
      'buttons':     buttons,
      'request_val': request_val
    }
  }
  return meta


def metaButtonObject(text='Button', set_command='', command_param='', command_value=''):
  meta = {
    'text':          text,
    'command':       set_command,
    'command_param': command_param,
    'command_value': command_value
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
    'data':    data
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
    'data':    data
  }
  return meta


def metaText(command=False, request=False, primary=False, title='text', text='', text_request='', context=''):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   title,
    'context': context,
    'type':    'text',
    'options': {
      'text':    text,
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


def metaWaterSensor(command=False, request=True, primary=False):
  meta = {
    'command': command,
    'request': request,
    'primary': primary,
    'title':   'water_level',
    'context': 'Is it full or empty',
    'type':    'text',
    'options': {
      CONTACT_OPEN:   "WET",
      CONTACT_CLOSED: "Dry"
    }
  }
  return meta


class ColorMap(object):
  def __init__(self, black=[], blue=[], green=[], red=[], yellow=[]):
    self.black = black
    self.blue = blue
    self.green = green
    self.red = red
    self.yellow = yellow

  def to_dict(self):
    return {
      COLOR_BLACK:  self.black,
      COLOR_BLUE:   self.blue,
      COLOR_GREEN:  self.green,
      COLOR_RED:    self.red,
      COLOR_YELLOW: self.yellow
    }


CAN_COMMAND = 'can_command'
CAN_REQUEST = 'can_request'
COLOR_MAPPING = 'color_mapping'
COMMAND = 'command'
COMMAND_PROP = 'command_prop'
COMMAND_VAL = 'command_val'
CONTEXT = 'context'
PRIMARY = 'primary'
REQUEST = 'request'
TEXT = 'text'
TEXT_MAPPING = 'text_mapping'
TITLE = 'title'
TYPE = 'type'

COLOR_BLACK = 'black'
COLOR_BLUE = 'blue'
COLOR_GREEN = 'green'
COLOR_RED = 'red'
COLOR_YELLOW = 'yellow'


def action_text(can_command=False, can_request=True, primary=False, title='', context='', request='', command='', command_prop='', command_val='', text_mapping={},
                color_mapping: ColorMap = ColorMap()):
  """Builds the action metadata for a text action.

  Args:
    can_command: Can you send a command to this kinda of action.
    can_request: Can you use this action in a trigger.
    primary: Is this the primary action.
    title: Title fot this action.
    context: Help context for this action.
    request: Request property for this action. (device.request_values[request])
    command: Command string for this action.
    command_prop: Command argument property.
    command_val: Reference to data to send with command.
    text_mapping: Text mapping dict.
    color_mapping: Color mapping object.

  Returns: dict of action.

  """
  action_metadata = {
    TYPE:          TEXT,
    CAN_COMMAND:   can_command,
    CAN_REQUEST:   can_request,
    PRIMARY:       primary,
    TITLE:         title,
    CONTEXT:       context,
    REQUEST:       request,
    COMMAND:       command,
    COMMAND_PROP:  command_prop,
    COMMAND_VAL:   command_val,
    TEXT_MAPPING:  text_mapping,
    COLOR_MAPPING: color_mapping.to_dict()
  }
  return action_metadata


def action_contact(primary=True, title='Contact sensor state', context='State of the door window sensor Open Close', request=CONTACT, text_mapping={
  'Open':   [CONTACT_OPEN],
  'Closed': [CONTACT_CLOSED]
}, color_mapping=ColorMap(green=[CONTACT_CLOSED], red=[CONTACT_OPEN])):
  action_meta = action_text(primary=primary, title=title, context=context, request=request, text_mapping=text_mapping, color_mapping=color_mapping)
  return action_meta
