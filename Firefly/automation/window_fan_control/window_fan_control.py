from uuid import uuid4

from Firefly import logging, scheduler
from Firefly.const import CONTACT, CONTACT_CLOSED, CONTACT_OPEN
from Firefly.helpers.automation import Automation
from Firefly.helpers.automation.automation_interface import AutomationInterface
from Firefly.helpers.automation.trigger_generators import generate_and_trigger, generate_or_trigger
from Firefly.helpers.device import TEMPERATURE
from Firefly.helpers.events import Command, Event, Request
from .metadata import METADATA


def Setup(firefly, package, **kwargs):
  if not kwargs.get('interface'):
    kwargs['interface'] = {}
  if not kwargs.get('metadata'):
    kwargs['metadata'] = METADATA
  else:
    kwargs['metadata'].update(METADATA)
  event_automation = WindowFanControl(firefly, package, **kwargs)
  # TODO: Replace this with a new firefly.add_device() function
  firefly.components[event_automation.id] = event_automation


class WindowFanControl(Automation):
  def __init__(self, firefly, package, **kwargs):
    logging.info('[WINDOW FAN] Starting Setup')
    interface_data = kwargs.get('interface', {})
    interface = AutomationInterface(firefly, 'not_set', interface_data)
    interface.build_interface(ignore_setup=True)

    window_open = {
      CONTACT: CONTACT_OPEN
    }
    window_closed = {
      CONTACT: CONTACT_CLOSED
    }

    lower_temp = {
      TEMPERATURE: [{
        'le': int(interface.temperature.get('low'))
      }]
    }
    upper_temp = {
      TEMPERATURE: [{
        'ge': int(interface.temperature.get('high'))
      }]
    }

    window_sensors = interface.sensors.get('windows')
    temp_sensors = interface.sensors.get(TEMPERATURE)

    window_opened_triggers = generate_and_trigger(window_open, window_sensors)
    window_closed_triggers = generate_or_trigger(window_closed, window_sensors)
    temp_low_triggers = generate_or_trigger(lower_temp, temp_sensors)
    temp_high_triggers = generate_or_trigger(upper_temp, temp_sensors)


    interface_data['triggers'] = {}
    interface_data['triggers']['windows_open'] = window_opened_triggers
    interface_data['triggers']['windows_closed'] = window_closed_triggers
    interface_data['triggers']['temp_low'] = temp_low_triggers
    interface_data['triggers']['temp_high'] = temp_high_triggers

    kwargs['interface'] = interface_data

    super().__init__(firefly, package, self.event_handler, **kwargs)

    self.timmer_id = str(uuid4())
    self.windows_open = False
    scheduler.runInS(10, self.check_start_state, job_id=self.timmer_id)


  def check_start_state(self):
    logging.info('[WINDOW FAN] checking starting state')
    if self.check_windows():
      self.windows_open = True
    current_temp = self.get_average_temperature()
    if current_temp <= self.new_interface.temperature.get('low'):
      self.switch_fans('off')
    if current_temp >= self.new_interface.temperature.get('high'):
      self.switch_fans('on')

  def switch_fans(self, state):
    logging.info('[WINDOW FAN] switching fan %s' % state)
    for fan in self.new_interface.switches.get('fans'):
      command = Command(fan, self.id, state)
      self.firefly.send_command(command)

  def check_windows(self):
    logging.info('[WINDOW FAN] checking windows')
    for window in self.new_interface.sensors.get('windows'):
      request = Request(window, self.id, CONTACT)
      contact_state = self.firefly.components[window].request(request)
      if contact_state == CONTACT_CLOSED:
        self.windows_open = False
        return False
    self.windows_open = True
    return True

  def get_average_temperature(self):
    logging.info('[WINDOW FAN] getting avg temp')
    total_temp = 0.0
    for sensor in self.new_interface.sensors.get(TEMPERATURE):
      request = Request(sensor, self.id, TEMPERATURE)
      total_temp += self.firefly.components[sensor].request(request)
    avg_temp = total_temp / len(self.new_interface.sensors.get(TEMPERATURE))
    logging.info('[WINDOW FAN] avg temp: %s' % str(avg_temp))
    return avg_temp

  def event_handler(self, event: Event = None, trigger_index="", **kwargs):
    logging.info('[WINDOW FAN] EVENT HANDLER: %s' % trigger_index)
    self.check_windows()
    if trigger_index == 'windows_open':
      self.check_start_state()
    if trigger_index == 'windows_closed':
      self.switch_fans('off')
      self.windows_open = False
      return
    if trigger_index == 'temp_low' and self.windows_open:
      avg_temp = self.get_average_temperature()
      if avg_temp > self.new_interface.temperature.get('low'):
        return
      delay = self.new_interface.delays.get('off')
      if delay:
        scheduler.runInS(delay, self.switch_fans, job_id=self.timmer_id, state='off')
      else:
        self.switch_fans('off')
    if trigger_index == 'temp_high' and self.windows_open:
      avg_temp = self.get_average_temperature()
      if avg_temp < self.new_interface.temperature.get('high'):
        return
      delay = self.new_interface.delays.get('on')
      if delay:
        scheduler.runInS(delay, self.switch_fans, job_id=self.timmer_id, state='on')
      else:
        self.switch_fans('on')

