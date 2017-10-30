from Firefly.const import (CONTACT, CONTACT_CLOSED, CONTACT_OPEN, EVENT_ACTION_OFF, EVENT_ACTION_ON, MOTION, MOTION_ACTIVE, MOTION_INACTIVE, NOT_PRESENT, PRESENCE, PRESENT, SENSOR_DRY, SENSOR_WET,
                           WATER)


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
  def __init__(self, black=[], blue=[], green=[], red=[], yellow=[], grey=[], orange=[]):
    self.black = black
    self.blue = blue
    self.green = green
    self.red = red
    self.yellow = yellow
    self.grey = grey
    self.orange = orange

  def to_dict(self):
    return {
      COLOR_BLACK:  self.black,
      COLOR_BLUE:   self.blue,
      COLOR_GREEN:  self.green,
      COLOR_RED:    self.red,
      COLOR_YELLOW: self.yellow,
      COLOR_GREY:   self.grey,
      COLOR_ORANGE: self.orange
    }


CAN_COMMAND = 'can_command'
CAN_REQUEST = 'can_request'
COLOR_MAPPING = 'color_mapping'
COMMAND = 'command'
COMMAND_PROP = 'command_prop'
COMMAND_VAL = 'command_val'
CONTEXT = 'context'
ICON = 'icon'
LEVEL_STEP = 'level_step'
MAX_LEVEL = 'max_level'
MIN_LEVEL = 'min_level'
PRIMARY = 'primary'
REQUEST = 'request'
SLIDER = 'slider'
SWITCH = 'switch'
TEXT = 'text'
TEXT_MAPPING = 'text_mapping'
TITLE = 'title'
TYPE = 'type'
SELECTED_VALUE = 'selected_value'
BUTTON = 'button'
BUTTON_GROUP = 'button_group'
BUTTON_LIST = 'button_list'

ON_COMMAND = 'on_command'
OFF_COMMAND = 'off_command'

COLOR_BLACK = 'black'
COLOR_BLUE = 'blue'
COLOR_GREEN = 'green'
COLOR_RED = 'red'
COLOR_YELLOW = 'goldenrod'
COLOR_GREY = 'grey'
COLOR_ORANGE = 'orange'


def action_switch(can_command=True, can_request=True, primary=False, title='', context='', request='', on_command=EVENT_ACTION_ON, off_command=EVENT_ACTION_OFF, color_mapping: ColorMap = ColorMap(),
                  icon='', **kwargs):
  """Builds the action metadata for a text action.

  Args:
    can_command: Can you send a command to this kinda of action.
    can_request: Can you use this action in a trigger.
    primary: Is this the primary action.
    title: Title fot this action.
    context: Help context for this action.
    request: Request property for this action. (device.request_values[request])
    on_command: command to send when setting on. (simple command)
    off_command: command to send when setting off. (simple command)
    color_mapping: Color mapping object.
    icon: string of icon to display for device.

  Returns: dict of action.

  """

  action_metadata = {
    CAN_COMMAND:   can_command,
    CAN_REQUEST:   can_request,
    COLOR_MAPPING: color_mapping.to_dict(),
    CONTEXT:       context,
    ICON:          icon,
    OFF_COMMAND:   off_command,
    ON_COMMAND:    on_command,
    PRIMARY:       primary,
    REQUEST:       request,
    TITLE:         title,
    TYPE:          SWITCH
  }

  return action_metadata


def action_on_off_switch(primary=True, title='Switch', context='On Off Controls for the switch', request='switch', on_command=EVENT_ACTION_ON, off_command=EVENT_ACTION_OFF,
                         color_mapping: ColorMap = ColorMap(green=[EVENT_ACTION_ON], grey=[EVENT_ACTION_OFF]), icon='ion-ios-bolt', **kwargs):
  return action_switch(primary=primary, title=title, context=context, request=request, on_command=on_command, off_command=off_command, color_mapping=color_mapping, icon=icon, **kwargs)


def action_text(can_command=False, can_request=True, primary=False, title='', context='', request='', command='', command_prop='', command_val='', text_mapping={}, icon='',
                color_mapping: ColorMap = ColorMap(), **kwargs):
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
    icon: string of icon to display for device.

  Returns: dict of action.

  """
  action_metadata = {
    CAN_COMMAND:   can_command,
    CAN_REQUEST:   can_request,
    COLOR_MAPPING: color_mapping.to_dict(),
    COMMAND:       command,
    COMMAND_PROP:  command_prop,
    COMMAND_VAL:   command_val,
    CONTEXT:       context,
    ICON:          icon,
    PRIMARY:       primary,
    REQUEST:       request,
    TEXT_MAPPING:  text_mapping,
    TITLE:         title,
    TYPE:          TEXT
  }
  return action_metadata


def action_contact(primary=True, title='Contact sensor state', context='State of the door window sensor Open Close', request=CONTACT, text_mapping={
  'Open':   [CONTACT_OPEN],
  'Closed': [CONTACT_CLOSED]
}, color_mapping=ColorMap(green=[CONTACT_CLOSED], red=[CONTACT_OPEN])):
  action_meta = action_text(primary=primary, title=title, context=context, request=request, text_mapping=text_mapping, color_mapping=color_mapping)
  return action_meta


def action_water_dry(primary=True, title='Water sensor state', context='Water detected? (Dry is Good)', request=WATER, text_mapping={
  'Dry': [SENSOR_DRY],
  'Wet': [SENSOR_WET]
}, color_mapping=ColorMap(green=[SENSOR_DRY], red=[SENSOR_WET])):
  action_meta = action_text(primary=primary, title=title, context=context, request=request, text_mapping=text_mapping, color_mapping=color_mapping)
  return action_meta


def action_presence(primary=True, title='Presence', context='Is this person at home', request=PRESENCE, text_mapping={
  'Home':     [PRESENT],
  'Not Home': [NOT_PRESENT]
}, color_mapping=ColorMap(green=[PRESENT], blue=[NOT_PRESENT])):
  action_meta = action_text(primary=primary, title=title, context=context, request=request, text_mapping=text_mapping, color_mapping=color_mapping)
  return action_meta


def action_motion(primary=True, title='Motion', context='State of the motion sensor', request=MOTION, text_mapping={
  'Active':   [MOTION_ACTIVE],
  'Inactive': [MOTION_INACTIVE]
}, color_mapping=ColorMap(blue=[MOTION_INACTIVE], red=[MOTION_ACTIVE])):
  action_meta = action_text(primary=primary, title=title, context=context, request=request, text_mapping=text_mapping, color_mapping=color_mapping)
  return action_meta


def action_level(can_command=True, can_request=True, primary=False, title='', context='', command='', command_prop='', request='', min_level=0, max_level=100, level_step=1, icon='', **kwargs):
  """Builds the action metadata for a text action.

  Args:
    can_command: Can you send a command to this kinda of action.
    can_request: Can you use this action in a trigger.
    command: Command to send
    command_prop: Key to send with slider level
    context: Help context for this action.
    icon: string of icon to display for device.
    primary: Is this the primary action.
    request: Request property for this action. (device.request_values[request])
    title: Title fot this action.
    level_min: min level of slider.
    level_max: max level of slider.
    level_step: step increment of slider.

  Returns: dict of action.

  """

  action_metadata = {
    CAN_COMMAND:  can_command,
    CAN_REQUEST:  can_request,
    COMMAND:      command,
    COMMAND_PROP: command_prop,
    CONTEXT:      context,
    ICON:         icon,
    LEVEL_STEP:   level_step,
    MAX_LEVEL:    max_level,
    MIN_LEVEL:    min_level,
    PRIMARY:      primary,
    REQUEST:      request,
    TITLE:        title,
    TYPE:         SLIDER,
  }

  return action_metadata


def action_dimmer(can_command=True, can_request=True, primary=False, title='Light Level', context='Set the level of the light', command='set_light', command_prop='level', request='level', min_level=0,
                  max_level=100, level_step=5, icon='', **kwargs):
  """Builds the action metadata for a text action.

  Args:
    can_command: Can you send a command to this kinda of action.
    can_request: Can you use this action in a trigger.
    command: Command to send
    command_prop: Key to send with slider level
    context: Help context for this action.
    icon: string of icon to display for device.
    primary: Is this the primary action.
    request: Request property for this action. (device.request_values[request])
    title: Title fot this action.
    level_min: min level of slider.
    level_max: max level of slider.
    level_step: step increment of slider.

  Returns: dict of action.

  """
  return action_level(can_command, can_request, primary, title, context, command, command_prop, request, min_level, max_level, level_step, icon, **kwargs)







######################################
# BUTTONS
######################################

def action_button_object(text='Button', command='', command_prop='', command_value='', selected_value='', **kwargs):
  ''' Create a button object.

  Args:
    text: Button text
    command: Command on press
    command_prop: Command pop to set
    command_value: Command value to set
    selected_value: Highlight button when request is this value
    **kwargs:

  Returns:

  '''
  button_object = {
    TEXT: text,
    COMMAND: command,
    COMMAND_PROP: command_prop,
    COMMAND_VAL: command_value,
    SELECTED_VALUE: selected_value
  }
  return button_object


def action_button_group(can_command=True, can_request=True, primary=False, title='Button Group', request='', buttons=[], **kwargs):
  ''' Make a button group

  Args:
    can_command: can send command
    can_request: can trigger
    primary: primary display
    title: title for buttons
    request: request value for selected button
    buttons: list of button objects
    **kwargs:

  Returns:

  '''
  action = {
    CAN_COMMAND: can_command,
    CAN_REQUEST: can_request,
    PRIMARY: primary,
    TITLE: title,
    REQUEST: request,
    TYPE: BUTTON_GROUP,
    BUTTON_LIST: buttons
  }
  return action
