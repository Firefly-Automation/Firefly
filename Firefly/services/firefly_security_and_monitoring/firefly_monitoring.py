"""
Firefly Security and Monitoring

This is the core Firefly Security and Monitoring Service. There should be almost zero config to the user and firefly will monitor the entire house.
- Alarm System (Away)
- Alarm System (Night)
- Vacation Lighting
- Battery Monitor
- Smoke Alerts
- Flooding Alerts
"""
from Firefly import logging, scheduler
from Firefly.helpers.events import Event, Command
from Firefly.helpers.device import BATTERY, CONTACT_CLOSE
from Firefly.services.firefly_security_and_monitoring.battery_monitor import check_battery_from_event, generate_battery_notification_message
from Firefly.services.firefly_security_and_monitoring.security_monitor import check_all_security_contact_sensors, generate_contact_warning_message, process_contact_change
from Firefly.const import SERVICE_NOTIFICATION, COMMAND_NOTIFY, SOURCE_LOCATION, TYPE_DEVICE
from .const import BATTERY_CRITICAL, BATTERY_LOW, BATTERY_NOTIFY_STATES, BATTERY_NO_NOTIFY_STATES

# TODO: Make this part of a config file
SECURE_MODES_NO_MOTION = ['night']
SECURE_MODES_MOTION = ['away']

class FireflySecurityAndMonitoring(object):
  def __init__(self, firefly, enabled=True):
    self.firefly = firefly

  def event(self, event: Event, **kwargs):
    logging.info('[FIREFLY SECURITY] event received: %s' % str(event))

    # Process Battery Notifications
    if BATTERY in event.event_action:
      self.process_battery_event(event)

    # Enter Secure Mode
    if event.source == SOURCE_LOCATION and 'mode' in event.event_action:
      mode = event.event_action['mode']
      if mode in SECURE_MODES_MOTION or mode in SECURE_MODES_NO_MOTION:
        self.enter_secure_mode()

    # Process Events while in secure mode
    mode = self.firefly.location.mode
    if mode in SECURE_MODES_NO_MOTION or mode in SECURE_MODES_MOTION:
      device = self.firefly.components[event.source]
      if device.type !=  TYPE_DEVICE:
        logging.info('[FIREFLY SECURITY] event source is not device')
        return
      if device.security:
        self.process_event_secure_mode(event)

  def process_event_secure_mode(self, event: Event):
    contact_data = process_contact_change(event)
    if contact_data['contact_event']:
      self.send_notification(contact_data['message'])
      if contact_data['alarm']:
        logging.info('[FIREFLY SECURITY] ALARM TRIGGERED')



  def enter_secure_mode(self, **kwargs):
    logging.info('[FIREFLY SECURITY] Entering Secure Mode.')
    # Grab snapshot of current state
    current_state = self.firefly.current_state.copy()
    components = self.firefly.components
    contact_states = check_all_security_contact_sensors(components, current_state)
    if contact_states[CONTACT_CLOSE]:
      message = generate_contact_warning_message(contact_states)
      self.send_notification(message)

  def process_battery_event(self, event: Event, **kwargs):
    battery_state = check_battery_from_event(event)
    if battery_state in BATTERY_NO_NOTIFY_STATES:
      if scheduler.cancel('%s_battery_notify' % event.source):
        self.send_notification('Battery in %s has been replaced.')
      return
    message = generate_battery_notification_message(event.source, battery_state)
    self.send_notification(message)
    if battery_state == BATTERY_LOW:
      return
    scheduler.runEveryH(4, self.send_notification, job_id='%s_battery_notify' % event.source, message=message)
    return

  def send_notification(self, message):
    notify = Command(SERVICE_NOTIFICATION, self.id, COMMAND_NOTIFY, message=message)
    self.firefly.send_command(notify)

  @property
  def id(self):
    return 'security_and_monitoring_service'


