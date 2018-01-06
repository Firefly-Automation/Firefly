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
from Firefly import logging, scheduler, aliases
from Firefly.const import COMMAND_NOTIFY, EVENT_TYPE_BROADCAST, FIREFLY_SECURITY_MONITORING, SERVICE_NOTIFICATION, SOURCE_LOCATION, TYPE_DEVICE, WATER, SENSOR_DRY, SENSOR_WET
from Firefly.helpers.device import BATTERY, CONTACT, CONTACT_CLOSE, CONTACT_OPEN, MOTION, MOTION_ACTIVE, MOTION_INACTIVE
from Firefly.helpers.events import Command, Event
from Firefly.services.firefly_security_and_monitoring.battery_monitor import check_battery_from_event, generate_battery_notification_message
from Firefly.services.firefly_security_and_monitoring.secueity_settings import FireflySecuritySettings
from Firefly.services.firefly_security_and_monitoring.security_monitor import (check_all_security_contact_sensors, check_all_security_motion_sensors, generate_contact_warning_message,
                                                                               process_contact_change, process_motion_change)
from Firefly.util.firefly_util import command_from_dict
from .const import ALARM_ARMED_MESSAGE_MOTION, ALARM_ARMED_MESSAGE_NO_MOTION, BATTERY_LOW, BATTERY_NO_NOTIFY_STATES, STATUS_TEMPLATE

ALARM_DISARMED = 'disarmed'
ALARM_ARMED = 'armed'
ALARM_ARMED_MOTION = 'armed_motion'
ALARM_ARMED_NO_MOTION = 'armed_no_motion'
ALARM_TRIGGERED = 'triggered'

SYSTEM_DISABLED = 'system_diabled'


class FireflySecurityAndMonitoring(object):
  def __init__(self, firefly, enabled=True):
    self.firefly = firefly
    self.enabled = enabled
    self.status = STATUS_TEMPLATE
    self.alarm_status = ALARM_DISARMED

    self.settings = FireflySecuritySettings()


  def shutdown(self, **kwargs):
    self.settings.save_config()

  def get_alarm_status(self, **kwargs):
    if not self.enabled:
      return SYSTEM_DISABLED
    return self.alarm_status

  def event(self, event: Event, **kwargs):
    logging.info('[FIREFLY SECURITY] event received: %s' % str(event))

    if not self.enabled:
      logging.info('[FIREFLY SECURITY] security and monitoring not enabled')
      return

    # Process Battery Notifications
    if BATTERY in event.event_action:
      self.process_battery_event(event)

    # Process water event only if monitoring is enabled for the device.
    if WATER in event.event_action:
      if self.check_security_enabled(event.source):
        self.process_water_event(event)

    # Enter Secure Mode
    if event.source == SOURCE_LOCATION and 'mode' in event.event_action:
      mode = event.event_action['mode']
      if self.check_secure_mode(mode):
        self.enter_secure_mode()

      # Exit secure mode
      last_mode = self.firefly.location.lastMode
      if not self.check_secure_mode(mode) and self.check_secure_mode(last_mode):
        self.alarm_status = ALARM_DISARMED
        self.status['status']['alarm'] = self.alarm_status
        self.firefly.update_security_firebase(self.status)
        self.send_notification('Security alarm disabled.')
        self.broadcast_status()
      return

    if event.source not in self.firefly.components:
      logging.info('[FIREFLY SECURITY] event source not in components: %s' % event.source)
      return

    # Process Events while in secure mode
    if self.check_secure_mode():
      if not self.check_security_enabled(event.source):
        logging.info('[FIREFLY SECURITY] event source is not device')
        return
      self.process_event_secure_mode(event)

    self.update_status(event)

  def startup(self, **kwargs):
    if self.check_secure_mode():
      self.enter_secure_mode()

  def check_secure_mode(self, mode=None, no_motion=True, motion=True):
    """

    Args:
      mode: The mode to check.
      no_motion: Check for modes with no motion active.
      motion: Check for modes with motion active.

    Returns: (bool) is in secure mode

    """
    if mode is None:
      mode = self.firefly.location.mode

    mode_secure_no_motion = mode in self.settings.secure_modes_no_motion
    mode_secure_motion = mode in self.settings.secure_modes_motion

    if no_motion and motion:
      return mode_secure_motion or mode_secure_no_motion
    elif no_motion:
      return mode_secure_no_motion
    elif motion:
      return mode_secure_motion
    return False

  # TODO: Move this into security monitor
  def generate_status(self, **kwargs):
    if not self.enabled:
      return

    contact_states = check_all_security_contact_sensors(self.firefly.components, self.firefly.current_state)
    motion_states = check_all_security_motion_sensors(self.firefly.components, self.firefly.current_state)

    status_data = {
      'status': {
        'message': 'Message Placeholder',
        'alarm':   self.alarm_status
      },
      CONTACT:  {
        'message':     '',
        CONTACT_OPEN:  {
          'count':                 len(contact_states[CONTACT_OPEN]),
          'devices': contact_states[CONTACT_OPEN]
        },
        CONTACT_CLOSE: {
          'count':                 len(contact_states[CONTACT_CLOSE]),
          'devices': contact_states[CONTACT_CLOSE]
        }
      },
      MOTION:   {
        'message':       '',
        MOTION_ACTIVE:   {
          'count':                len(motion_states[MOTION_ACTIVE]),
          'devices': motion_states[MOTION_ACTIVE]
        },
        MOTION_INACTIVE: {
          'count':                len(motion_states[MOTION_INACTIVE]),
          'devices': motion_states[MOTION_INACTIVE]
        }
      }
    }
    self.status = status_data
    self.firefly.update_security_firebase(self.status)

  def check_security_enabled(self, ff_id: str, filter_type=TYPE_DEVICE) -> bool:
    if ff_id not in self.firefly.components:
      logging.info('[FIREFLY SECURITY] component not found: %s' % ff_id)
      return False

    try:
      component = self.firefly.components[ff_id]
      return component.security and component.type == filter_type
    except:
      return False

  # TODO: Move this into security monitor
  def update_status(self, event: Event):
    ff_id = event.source
    if not self.check_security_enabled(ff_id):
      return

    # Update Contact Status
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

    # Update Motion Status
    if MOTION in event.event_action:
      if event.event_action[MOTION] == MOTION_ACTIVE:
        self.status[MOTION][MOTION_ACTIVE]['devices'].append(ff_id)
        self.status[MOTION][MOTION_ACTIVE]['count'] = len(self.status[MOTION][MOTION_ACTIVE]['devices'])
        try:
          self.status[MOTION][MOTION_INACTIVE]['devices'].remove(ff_id)
          self.status[MOTION][MOTION_INACTIVE]['count'] = len(self.status[MOTION][MOTION_INACTIVE]['devices'])
        except Exception as e:
          logging.error('[FIREFLY SECURITY] error updating status: %s' % e)

      if event.event_action[MOTION] == MOTION_INACTIVE:
        self.status[MOTION][MOTION_INACTIVE]['devices'].append(ff_id)
        self.status[MOTION][MOTION_INACTIVE]['count'] = len(self.status[MOTION][MOTION_INACTIVE]['devices'])
        try:
          self.status[MOTION][MOTION_ACTIVE]['devices'].remove(ff_id)
          self.status[MOTION][MOTION_ACTIVE]['count'] = len(self.status[MOTION][MOTION_ACTIVE]['devices'])
        except Exception as e:
          logging.error('[FIREFLY SECURITY] error updating status: %s' % e)

    self.firefly.update_security_firebase(self.status)

  def process_event_secure_mode(self, event: Event):
    alarm_triggered = False
    contact_data = process_contact_change(event)
    if contact_data['contact_event']:
      self.send_notification(contact_data['message'])
      if contact_data['alarm']:
        alarm_triggered = True
        logging.info('[FIREFLY SECURITY] ALARM TRIGGERED')
        # TODO: Turn on listed lights, if no lights listed then turn on all lights

    if self.check_secure_mode(no_motion=False):
      motion_data = process_motion_change(event)
      if motion_data['alarm']:
        alarm_triggered = True
        self.send_notification(motion_data['message'])
        logging.info('[FIREFLY SECURITY] ALARM TRIGGERED')

    if alarm_triggered:
      self.trigger_alarm()

  def trigger_alarm(self, **kwargs):
    logging.info('TRIGGERING ALARM')
    self.alarm_status = ALARM_TRIGGERED
    lights = self.settings.lights
    if not lights:
      lights = self.get_devices_by_tag()

    for ff_id in lights:
      command = command_from_dict(ff_id, self.id, self.settings.light_command)
      logging.info('FIREFLY SECURITY] sending command %s' % str(command))
      self.firefly.send_command(command)

    alarms = self.settings.alarms
    if not alarms:
      alarms = self.get_devices_by_tag(tags=['alarm'])

    for ff_id in alarms:
      command = Command(ff_id, self.id, self.settings.alarm_command)
      self.firefly.send_command(command)

    self.broadcast_status()
    self.status['status']['alarm'] = self.alarm_status.replace('_', ' ')
    self.firefly.update_security_firebase(self.status)

  def enter_secure_mode(self, **kwargs):
    logging.info('[FIREFLY SECURITY] Entering Secure Mode.')
    # Grab snapshot of current state
    current_state = self.firefly.current_state.copy()
    components = self.firefly.components
    contact_states = check_all_security_contact_sensors(components, current_state)
    if contact_states[CONTACT_OPEN]:
      message = generate_contact_warning_message(contact_states)
      self.send_notification(message)

    # If no contacts open then send notification that alarm is now armed.
    if self.check_secure_mode(no_motion=False):
      self.send_notification(ALARM_ARMED_MESSAGE_MOTION)
      self.alarm_status = ALARM_ARMED_MOTION
    else:
      self.send_notification(ALARM_ARMED_MESSAGE_NO_MOTION)
      self.alarm_status = ALARM_ARMED_NO_MOTION

    self.status['status']['alarm'] = self.alarm_status.replace('_', ' ')
    self.firefly.update_security_firebase(self.status)
    self.broadcast_status()



  def broadcast_status(self, **kwargs):
    event = Event(self.id, EVENT_TYPE_BROADCAST, {
      'status': self.alarm_status,
    })
    self.firefly.send_event(event)

  def get_devices_by_tag(self, tags=['light'], **kwargs):
    devices = []
    for ff_id, component in self.firefly.components.items():
      if component.type != TYPE_DEVICE:
        continue
      try:
        for tag in component.tags:
          if tag in tags:
            devices.append(ff_id)
            continue
      except:
        pass
    return devices


  def process_water_event(self, event: Event, **kwargs):
    alias = aliases.get_alias(event.source)
    if event.event_action.get(WATER) == SENSOR_WET:
      self.send_notification('ALERT!!! Water detected by: %s' % alias)
      self.trigger_alarm()
      return
    if event.event_action.get(WATER) == SENSOR_DRY:
      self.send_notification('ALERT!!! Water no longer detected by: %s' % alias)
      return

  def process_battery_event(self, event: Event, **kwargs):
    (battery_state, battery_level) = check_battery_from_event(event)
    if battery_state in BATTERY_NO_NOTIFY_STATES:
      if scheduler.cancel('%s_battery_notify' % event.source):
        self.send_notification('Battery in %s has been replaced.')
      return
    message = generate_battery_notification_message(event.source, battery_state, battery_level)
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
    return FIREFLY_SECURITY_MONITORING
