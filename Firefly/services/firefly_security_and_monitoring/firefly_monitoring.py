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
from Firefly.const import COMMAND_NOTIFY, SERVICE_NOTIFICATION, SOURCE_LOCATION, TYPE_DEVICE
from Firefly.helpers.device import BATTERY, CONTACT, CONTACT_CLOSE, CONTACT_OPEN
from Firefly.helpers.events import Command, Event
from Firefly.services.firefly_security_and_monitoring.battery_monitor import check_battery_from_event, generate_battery_notification_message
from Firefly.services.firefly_security_and_monitoring.security_monitor import check_all_security_contact_sensors, generate_contact_warning_message, process_contact_change
from Firefly.services.firefly_security_and_monitoring.secueity_settings import FireflySecuritySettings
from .const import BATTERY_LOW, BATTERY_NO_NOTIFY_STATES, STATUS_TEMPLATE, ALARM_ARMED_MESSAGE_MOTION, ALARM_ARMED_MESSAGE_NO_MOTION


class FireflySecurityAndMonitoring(object):
  def __init__(self, firefly, enabled=True):
    self.firefly = firefly
    self.enabled = enabled
    self.status = STATUS_TEMPLATE

    self.settings = FireflySecuritySettings()

  def event(self, event: Event, **kwargs):
    logging.info('[FIREFLY SECURITY] event received: %s' % str(event))

    if not self.enabled:
      logging.info('[FIREFLY SECURITY] security and monitoring not enabled')
      return

    # Process Battery Notifications
    if BATTERY in event.event_action:
      self.process_battery_event(event)

    # Enter Secure Mode
    if event.source == SOURCE_LOCATION and 'mode' in event.event_action:
      mode = event.event_action['mode']
      if mode in self.settings.secure_modes_motion or mode in self.settings.secure_modes_no_motion:
        self.enter_secure_mode()

    # Process Events while in secure mode
    mode = self.firefly.location.mode
    if mode in self.settings.secure_modes_motion or mode in self.settings.secure_modes_no_motion:
      device = self.firefly.components[event.source]
      if device.type != TYPE_DEVICE:
        logging.info('[FIREFLY SECURITY] event source is not device')
        return
      if device.security:
        self.process_event_secure_mode(event)

    self.update_status(event)

  def generate_status(self, **kwargs):
    if not self.enabled:
      return

    contact_states = check_all_security_contact_sensors(self.firefly.components, self.firefly.current_state)
    status_data = {
      CONTACT: {
        CONTACT_OPEN:  {
          'count':                 len(contact_states[CONTACT_OPEN]),
          'devices': contact_states[CONTACT_OPEN]
        },
        CONTACT_CLOSE: {
          'count':                 len(contact_states[CONTACT_CLOSE]),
          'devices': contact_states[CONTACT_CLOSE]
        }
      }
    }
    self.status = status_data
    self.firefly.update_security_firebase(self.status)

  def check_security_enabled(self, ff_id: str, filter_type=TYPE_DEVICE) -> bool:
    try:
      component = self.firefly.components[ff_id]
      return component.security and component.type == filter_type
    except:
      return False

  def update_status(self, event: Event):
    ff_id = event.source
    if not self.check_security_enabled(ff_id):
      return

    if CONTACT in event.event_action:
      if event.event_action[CONTACT] == CONTACT_OPEN:
        self.status[CONTACT][CONTACT_OPEN]['devices'].append(ff_id)
        self.status[CONTACT][CONTACT_OPEN]['count'] = len(self.status[CONTACT][CONTACT_OPEN]['devices'])
        try:
          self.status[CONTACT][CONTACT_CLOSE]['devices'].remove(ff_id)
          self.status[CONTACT][CONTACT_CLOSE]['count'] = len(self.status[CONTACT][CONTACT_CLOSE]['devices'])
        except Exception as e:
          logging.error('[FIREFLY SECURITY] error updating status: %s' % e)

      if event.event_action[CONTACT] == CONTACT_CLOSE:
        self.status[CONTACT][CONTACT_CLOSE]['devices'].append(ff_id)
        self.status[CONTACT][CONTACT_CLOSE]['count'] = len(self.status[CONTACT][CONTACT_CLOSE]['devices'])
        try:
          self.status[CONTACT][CONTACT_OPEN]['devices'].remove(ff_id)
          self.status[CONTACT][CONTACT_OPEN]['count'] = len(self.status[CONTACT][CONTACT_OPEN]['devices'])
        except Exception as e:
          logging.error('[FIREFLY SECURITY] error updating status: %s' % e)

    self.firefly.update_security_firebase(self.status)

  def process_event_secure_mode(self, event: Event):
    contact_data = process_contact_change(event)
    if contact_data['contact_event']:
      self.send_notification(contact_data['message'])
      if contact_data['alarm']:
        logging.info('[FIREFLY SECURITY] ALARM TRIGGERED')
        # TODO: Turn on listed lights, if no lights listed then turn on all lights

  def enter_secure_mode(self, **kwargs):
    logging.info('[FIREFLY SECURITY] Entering Secure Mode.')
    # Grab snapshot of current state
    current_state = self.firefly.current_state.copy()
    components = self.firefly.components
    contact_states = check_all_security_contact_sensors(components, current_state)
    if contact_states[CONTACT_OPEN]:
      message = generate_contact_warning_message(contact_states)
      self.send_notification(message)
      return

    # If no contacts open then send notification that alarm is now armed.
    if self.firefly.location.mode in self.settings.secure_modes_motion:
      self.send_notification(ALARM_ARMED_MESSAGE_MOTION)
      return
    self.send_notification(ALARM_ARMED_MESSAGE_NO_MOTION)

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
