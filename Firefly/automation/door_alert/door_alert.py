from .metadata import METADATA, AUTHOR, TITLE
from Firefly import logging, scheduler
from Firefly.helpers.automation import Automation
from uuid import uuid4
from Firefly.helpers.events import Event, Request, Command

# TODO(zpriddy): These should be in const file
LABEL_TRIGGERS = 'triggers'

def Setup(firefly, package, **kwargs):
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  else:
    kwargs['metadata'].update(METADATA)
  door_alert = DoorAlert(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[door_alert.id] = door_alert

class DoorAlert(Automation):
  def __init__(self, firefly, package, **kwargs):
    # TODO: Make this part of the Automation class..
    interface = kwargs.get('interface')
    triggers = self.build_triggers_from_device_list(interface)
    interface['triggers'] = triggers
    kwargs['interface'] = interface

    logging.info('door alert interface: %s' % str(interface))
    self.lights = interface.get('devices', {}).get('lights', [])

    super().__init__(firefly, package, self.event_handler, **kwargs)

    self.triggered = False
    self.timer_id = str(uuid4())

    # TODO(zpriddy): Fix this is firebase service
    self._title = TITLE
    self._package = self.package
    self._alias = self.alias

    self.light_state = {}
    self.flash_timer_id = str(uuid4())


  def event_handler(self, event: Event=None, trigger_index="", **kwargs):
    logging.info('[DOOR ALERT] EVENT HANDLER: %s' % trigger_index)
    if trigger_index == "initial":
      self.initial_event_handler(event, trigger_index)
    if trigger_index == "delayed":
      self.delayed_event_handler(event, trigger_index)

  def initial_event_handler(self, event: Event = None, trigger_index="initial", skip_delay=False, **kwargs):
    """ Handle the initial event trigger.
    Args:
      event: (Event) The event that triggered the handler.
      trigger_index: (str) Trigger index (key) in the metadata.
      skip_delay: (bool) Skip the initial delay. This is used in case there is an initial delay, the delayed function will call this function and tell it to skip the initial delay.
      **kwargs:
    """
    # If it's the first time getting triggered then send the message.
    # If it has already been triggered then cancel the current delayed action timer.
    if not skip_delay and not self.triggered and self.new_interface.delays.get(trigger_index):
      logging.info('[DOOR ALERT] STARTING TIMER')
      scheduler.runInS(self.new_interface.delays.get(trigger_index), self.initial_event_handler, self.timer_id, True, event=event, trigger_index=trigger_index, skip_delay=True)
      return
    if skip_delay and not self.triggered:
      self.start(trigger_index)
      return
    #if self.triggered:
    #  scheduler.cancel(self.timer_id)


  def delayed_event_handler(self, event: Event = None, trigger_index="delayed", **kwargs):
    # If it has not been triggered then stop.
    if not self.triggered:
      # Cancel timer if it's currently waiting for initial delay.
      scheduler.cancel(self.timer_id)
      return
    # If there is a delay, wait for the delay and then execute, otherwise execute.
    if self.delays.get(trigger_index):
      scheduler.runInS(self.new_interface.delays.get(trigger_index), self.stop, self.timer_id, True, trigger_index=trigger_index)
    else:
      self.stop(trigger_index)


  def start(self, trigger_index='initial', **kwargs):
    logging.info('[DOOR ALERT START]')
    self.triggered =True
    self.send_messages(trigger_index)

    for light in self.lights:
      self.light_state[light] = self.firefly.components[light].request(Request(light, self.id, 'switch'))

    logging.info('[DOOR ALERT] %s' % str(self.light_state))
    self.flash('off')


  def stop(self, trigger_index='delayed', **kwargs):
    logging.info('[DOOR ALERT END]')
    self.triggered =False
    self.send_messages(trigger_index)

    for light, switch in self.light_state.items():
      self.firefly.send_command(Command(light, self.id, switch))


  def flash(self, switch='on'):
    if not self.triggered:
      return
    next_switch = 'off' if switch == 'on' else 'on'
    for light in self.lights:
      self.firefly.send_command(Command(light,self.id,switch))
    scheduler.runInS(2, self.flash, job_id=self.flash_timer_id, switch=next_switch)





  #TODO: Make this part of the Automation class..
  def build_triggers_from_device_list(self, interface):
    device_ids = interface.get('devices', {}).get('contact_sensors', [])
    triggers_initial = []
    triggers_delayed = []
    for device in device_ids:
      triggers_initial.append([{
        'listen_id': device,
        'source': 'SOURCE_TRIGGER',
        'trigger_action': [{
          'contact': 'open'
        }]
      }])
      triggers_delayed.append({
        'listen_id': device,
        'source': 'SOURCE_TRIGGER',
        'trigger_action': [{
          'contact': 'close'
        }]
      })
    return {'initial':triggers_initial, 'delayed':[triggers_delayed]}