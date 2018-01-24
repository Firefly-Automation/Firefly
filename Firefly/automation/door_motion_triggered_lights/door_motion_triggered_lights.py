from uuid import uuid4

from Firefly import logging, scheduler
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN, MOTION, MOTION_ACTIVE, MOTION_INACTIVE
from Firefly.helpers.automation import Automation
from Firefly.helpers.automation.automation_interface import AutomationInterface
from Firefly.helpers.automation.trigger_generators import generate_and_trigger, generate_or_trigger
from Firefly.helpers.events import Command, Event
from .metadata import METADATA


def Setup(firefly, package, **kwargs):
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  else:
    kwargs['metadata'].update(METADATA)
  event_automation = DoorMotionLights(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[event_automation.id] = event_automation


class DoorMotionLights(Automation):
  def __init__(self, firefly, package, **kwargs):
    interface_data = kwargs.get('interface', {})
    interface = AutomationInterface(firefly, 'not_set', interface_data)
    interface.build_interface(ignore_setup=True)

    door_open = {
      CONTACT: CONTACT_OPEN
    }
    door_closed = {
      CONTACT: CONTACT_CLOSED
    }
    motion_active = {
      MOTION: MOTION_ACTIVE
    }
    motion_inactive = {
      MOTION: MOTION_INACTIVE
    }

    contact_sensors = interface.sensors.get('doors')
    motion_sensors = interface.sensors.get('motion')

    interface_data['triggers'] = {}
    motion_active_triggers = generate_or_trigger(motion_active, motion_sensors)
    door_open_triggers = generate_or_trigger(door_open, contact_sensors)
    interface_data['triggers']['on'] = motion_active_triggers + door_open_triggers

    motion_inactive_triggers = generate_and_trigger(motion_inactive, motion_sensors)[0]
    door_closed_triggers = generate_and_trigger(door_closed, contact_sensors)[0]
    interface_data['triggers']['off'] = [motion_inactive_triggers + door_closed_triggers]

    kwargs['interface'] = interface_data

    super().__init__(firefly, package, self.event_handler, **kwargs)

    self.timmer_id = str(uuid4())

  def event_handler(self, event: Event = None, trigger_index="", **kwargs):
    logging.info('[DOOR MOTION TRIGGER] EVENT HANDLER: %s' % trigger_index)
    scheduler.cancel(self.timmer_id)

    if trigger_index == 'on':
      actions = self.new_interface.actions.get('on')
      if actions:
        self.execute_actions(trigger_index)
      else:
        command = self.new_interface.commands.get('on')
        for light in self.new_interface.lights.get('lights'):
          c = Command(light, self.id, command)
          self.firefly.send_command(c)

    if trigger_index == 'off':
      if self.new_interface.delays.get('off'):
        scheduler.runInS(self.new_interface.delays.off, self.set_off, job_id=self.timmer_id)
      else:
        self.set_off()

  def set_off(self, **kwargs):
    actions = self.new_interface.actions.get('off')
    if actions:
      self.execute_actions("off")
    else:
      command = self.new_interface.commands.get('off')
      for light in self.new_interface.lights.get('lights'):
        c = Command(light, self.id, command)
        self.firefly.send_command(c)
