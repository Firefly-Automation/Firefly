from Firefly import logging
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN
from Firefly.helpers.device import *
from Firefly.helpers.device.device import Device
from Firefly.helpers.metadta.metadata import action_contact, action_text


ALARM = 'alarm'
DEVICE_TYPE_CONTACT_SENSOR = 'contact_sensor'

COMMANDS = []

REQUESTS = [ALARM, BATTERY, CONTACT]

CAPABILITIES = {
  ALARM:   False,
  BATTERY: False,
  CONTACT: False,
}

INITIAL_VALUES = {
  '_alarm':   False,
  '_battery': -1,
  '_contact': CONTACT_CLOSED
}


class ContactSensor(Device):
  def __init__(self, firefly, package, title, author, commands=COMMANDS, requests=REQUESTS, device_type=DEVICE_TYPE_CONTACT_SENSOR, capabilities=CAPABILITIES, initial_values=INITIAL_VALUES, **kwargs):
    logging.message('SETTING UP MULTI_SENSOR')
    INITIAL_VALUES.update(initial_values)
    initial_values = INITIAL_VALUES
    super().__init__(firefly, package, title, author, commands, requests, device_type, initial_values=initial_values, **kwargs)

    if capabilities[ALARM] and ALARM in requests:
      self.add_request(ALARM, self.get_alarm)
      self.add_action(ALARM, action_text(title='Alarm Code', context='Alarm code from device', request=ALARM))

    if capabilities[BATTERY] and BATTERY in requests:
      self.add_request(BATTERY, self.get_battery)
      self.add_action(BATTERY, action_text(title='Battery',context='Battery Level', request=BATTERY))

    if capabilities[CONTACT] and CONTACT in requests:
      self.add_request(CONTACT, self.get_contact)
      self.add_action(CONTACT, action_contact(primary=True))
      if 'contact' not in self.tags:
        self._tags.append('contact')

    self._alexa_export = False
    self.capabilities = CAPABILITIES

  def update_values(self, alarm=None, battery=None, contact=None, **kwargs):
    if alarm is not None:
      self._alarm = alarm
    if battery is not None:
      self._battery = battery
    if contact is not None:
      if type(contact) is str:
        self._contact = contact
      if type(contact) is bool:
        self._contact = CONTACT_OPEN if contact else CONTACT_CLOSED

  def get_battery(self, **kwargs):
    return self._battery

  def get_contact(self, **kwargs):
    return self._contact

  def get_alarm(self, **kwargs):
    return self._alarm
