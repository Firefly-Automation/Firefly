from Firefly import logging
from Firefly.helpers.automation import Automation
from Firefly.helpers.events import Command, Event
from Firefly.const import SERVICE_NOTIFICATION, COMMAND_NOTIFY, AUTHOR

TITLE = 'Firefly Routines'
COMMANDS = ['execute']
METADATA = {
  'title':     TITLE,
  'author':    AUTHOR,
  'commands':  COMMANDS,
  'interface': {
    'actions':   {
      "routine": {
        'context': 'Actions to be executed when routine runs.',
        'type':    'commandList'
      }
    },
    'messages':  {
      "routine": {
        'context': 'Message to be sent when routine executes.',
        'type':    'string'
      }
    },
    'mode':      {
      "routine": {
        'context': 'Mode to be set when routine executes.',
        'type':    'modeString'
      }
    },
    'icon':      {
      "routine": {
        'context': 'Name of icon to be displayed on UI.',
        'type':    'iconString'
      }
    },
    'export_ui': {
      "routine": {
        'context': 'Display routine on web interface.',
        'type':    'boolean'
      }
    },
    'triggers':  {
      "routine": {
        'context': 'Actions that will trigger the routine',
        'type':    'triggerList'
      }
    },
  }
}


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine' % package)
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  routine = Routine(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[routine.id] = routine


class Routine(Automation):
  def __init__(self, firefly, package, **kwargs):
    super().__init__(firefly, package, self.event_handler, **kwargs)

    # TODO(zpriddy): Fix this is firebase service
    self._title = TITLE
    self._package = self.package
    self._alias = self.alias

    try:
      self.mode = self.interface.get('mode').get("routine")
    except:
      self.mode = None

    try:
      self.icon = self.interface.get('icon').get("routine", 'new_releases')
    except:
      self.icon = 'new_releases'

    try:
      self.export_ui = self.interface.get('export_ui').get("routine", True)
    except:
      self.export_ui = False

    self.add_command('execute', self.event_handler)

  def export(self, **kwargs):
    if kwargs.get('firebase_view'):
      return self.get_view(**kwargs)

    export_data = super().export()
    export_data['interface']['icon'] = {}
    export_data['interface']['icon']["routine"] = self.icon
    export_data['interface']['export_ui'] = {}
    export_data['interface']['export_ui']["routine"] = self.export_ui
    if self.mode:
      export_data['interface']['mode'] = {}
      export_data['interface']['mode']["routine"] = self.mode

    return export_data

  def get_view(self, **kwargs):
    view_data = {
      'ff_id': self.id,
      'alias': self.alias,
      'icon':  self.icon,
      'command': 'execute',
      'export_ui': self.export_ui
    }
    return view_data

  def event_handler(self, event: Event = None, trigger_index=0, **kwargs):
    if self.messages.get("routine"):
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self.messages["routine"])
      self.firefly.send_command(notify)

    if self.mode:
      self.firefly.location.mode = self.mode

    if self.actions.get("routine"):
      for a in self.actions["routine"]:
        a.execute_action(self.firefly)
    return True
