from Firefly import logging
from Firefly.automation.const import AUTOMATION_INTERFACE
from Firefly.automation.routine.const import ROUTINE_EXECUTE, ROUTINE_ICON, ROUTINE_MODE, ROUTINE_ROUTINE
from Firefly.automation.routine.metadata import METADATA, TITLE
from Firefly.const import COMMAND_NOTIFY, SERVICE_NOTIFICATION, TYPE_ROUTINE
from Firefly.helpers.automation import Automation
from Firefly.helpers.automation.automation_interface import AutomationInterface
from Firefly.helpers.events import Command, Event

# TODO: Routines should take a list of lights to turn off and a list of lights to user definable value.

SUNRISE_TRIGGER = [[{
  "listen_id":      "location",
  "source":         "SOURCE_TRIGGER",
  "trigger_action": [{
    "location": ["sunrise"]
  }]
}]]
SUNSET_TRIGGER = [[{
  "listen_id":      "location",
  "source":         "SOURCE_TRIGGER",
  "trigger_action": [{
    "location": ["sunset"]
  }]
}]]


def Setup(firefly, package, **kwargs):
  logging.message('Entering %s setup Routine' % package)
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  # if kwargs.get('metadata'):
  #  METADATA.update(kwargs['metadata'])
  kwargs['metadata'] = METADATA
  routine = Routine(firefly, package, **kwargs)
  return firefly.install_component(routine)


class Routine(Automation):
  def __init__(self, firefly, package, **kwargs):
    interface_data = kwargs.get('interface', {})
    logging.info('[INTERFACE DATA] %s' % str(interface_data))
    if not interface_data['triggers']:
      interface_data['triggers'] = {}
    interface_data['triggers']['sunrise'] = SUNRISE_TRIGGER
    interface_data['triggers']['sunset'] = SUNSET_TRIGGER

    logging.info('[INTERFACE DATA] %s' % str(interface_data))

    kwargs['interface'] = interface_data

    super().__init__(firefly, package, self.event_handler, **kwargs)

    # TODO(zpriddy): Fix this is firebase service
    self._title = TITLE
    self._package = self.package
    self._alias = self.alias

    # TODO: Change these to self.interface.settings.mode and interface.settings.icon
    self.mode = self.new_interface.mode.get(ROUTINE_ROUTINE, None)
    self.icon = self.new_interface.icon.get(ROUTINE_ROUTINE, '')
    self.export_ui = self.new_interface.export_ui.get(ROUTINE_ROUTINE, True)

    # TODO: replace export_ui with a const from metadata or core.
    # self.export_ui = self.interface.get('export_ui', {}).get(ROUTINE_ROUTINE, True)

    self.add_command(ROUTINE_EXECUTE, self.event_handler)

  def export(self, **kwargs):
    if kwargs.get('firebase_view'):
      return self.get_view(**kwargs)

    export_data = super().export()
    export_data[AUTOMATION_INTERFACE][ROUTINE_ICON] = {
      ROUTINE_ROUTINE: self.icon
    }
    # TODO: replace export_ui with a const from metadata or core.
    export_data[AUTOMATION_INTERFACE]['export_ui'] = {
      ROUTINE_ROUTINE: self.export_ui
    }
    if self.mode:
      export_data[AUTOMATION_INTERFACE][ROUTINE_MODE] = {
        ROUTINE_ROUTINE: self.mode
      }

    return export_data

  def get_view(self, **kwargs):
    view_data = {
      'ff_id':     self.id,
      'alias':     self.alias,
      'icon':      self.icon,
      'command':   'execute',
      'export_ui': self.export_ui
    }
    return view_data

  def event_handler(self, event: Event = None, trigger_index=0, **kwargs):
    if (trigger_index == 'sunrise' and self.new_interface.auto_transition.get('sunrise', True)) or (trigger_index == 'sunset' and self.new_interface.auto_transition.get('sunset', True)):
      if self.new_interface.actions.get(ROUTINE_ROUTINE):
        for a in self.new_interface.actions.get(ROUTINE_ROUTINE):
          a.execute_action(self.firefly)

      self.handle_off_commands()
      self.handle_on_commands()

      return True


    if self.mode == self.firefly.location.mode:
      logging.info('[ROUTINE] not executing because already in mode.')
      return False

    if self.new_interface.messages.get(ROUTINE_ROUTINE):
      notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=self.new_interface.messages.get(ROUTINE_ROUTINE))
      self.firefly.send_command(notify)

    if self.mode:
      self.firefly.location.mode = self.mode

    if self.new_interface.actions.get(ROUTINE_ROUTINE):
      for a in self.new_interface.actions.get(ROUTINE_ROUTINE):
        a.execute_action(self.firefly)

    self.handle_off_commands()
    self.handle_on_commands()

    return True

  def handle_on_commands(self):
    self.handle_on_off_command('on', 'on')

    if self.firefly.location.isDark:
      self.handle_on_off_command('on_night', 'on')
    else:
      self.handle_on_off_command('on_day', 'on')

  def handle_off_commands(self):
    self.handle_on_off_command('off', 'off')

    if self.firefly.location.isDark:
      self.handle_on_off_command('off_night', 'off')
    else:
      self.handle_on_off_command('off_day', 'off')

  def handle_on_off_command(self, command_index, default_command):
    logging.info('ROUTINE DEBUG COMMAND INDEX: %s' % command_index)
    command = self.new_interface.commands.get(command_index)
    logging.info('ROUTINE DEBUG COMMAND: %s' % command)
    logging.info('ROUTINE DEBUG COMMAND: %s' % bool(command))

    if not command:
      logging.info('ROUTINE DEBUG NO COMMAND - DOING DEFAULT')
      lights = self.new_interface.lights.get(command_index)
      if lights:
        for light in lights:
          self.firefly.send_command(Command(light, self.id, default_command))

    else:
      logging.info('ROUTINE DEBUG COMMAND - DOING CUSTOM COMMAND')
      set_command = list(command.keys())[0]
      command_args = list(command.values())[0]
      logging.info('ROUTINE DEBUG COMMAND: %s' % set_command)
      lights = self.new_interface.lights.get(command_index)
      if lights:
        for light in lights:
          self.firefly.send_command(Command(light, self.id, set_command, **command_args))

  def get_alexa_view(self, **kwargs):
    if self.export_ui is False:
      return None

    return {
      'endpointId':        self.id,
      'manufacturerName':  'Firefly Home',
      'friendlyName':      self.alias,
      'description':       'A Firefly Home Scene',
      'displayCategories': ['SCENE_TRIGGER'],
      'cookie':            {},
      'capabilities':      [
        {
          'type':                 'AlexaInterface',
          'interface':            'Alexa.SceneController',
          'version':              '3',
          'supportsDeactivation': False,
          'proactivelyReported':  True
        }
      ]
    }

  @property
  def type(self):
    return TYPE_ROUTINE
