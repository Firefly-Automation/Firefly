from Firefly.helpers import logging
from Firefly import aliases
from typing import TypeVar
from Firefly.const import (EVENT_TYPE_COMMAND, COMMAND_NOTIFY, COMMAND_SPEECH, COMMAND_ROUTINE, EVENT_TYPE_REQUEST)

COMMAND_TYPE = TypeVar('COMMAND', dict, str)


class Event(object):
  """
  Events are messages sent between apps and devices. Events can carry requests, commands, or updates.
  """

  def __init__(self, source: str, event_type: str, event_action: str = '', **kwargs):
    self._source = source
    self._event_type = event_type
    self._event_action = event_action
    self._kwargs = kwargs

  def __str__(self):
    return '<FIREFLY EVENT - SOURCE: %s | TYPE: %s | ACTION: %s >' % (self.source, self.event_type, self.event_action)

  @property
  def source(self):
    return self._source

  @property
  def event_type(self):
    return self._event_type

  @property
  def event_action(self):
    return self._event_action


class Command(Event):
  """
  Class for holding a command.
  """

  def __init__(self, device, source: str, command: COMMAND_TYPE, command_action: str = '', force=False, **kwargs):
    Event.__init__(self, source, EVENT_TYPE_COMMAND)
    self._command = command
    self._command_action = command_action
    self._device = aliases.get_device_id(device)
    self._force = force
    self._args = kwargs
    self._simple_command = True if type(command) == str else False
    self._is_notify = True if command_action == COMMAND_NOTIFY else False
    self._is_speech = True if command_action == COMMAND_SPEECH else False
    self._is_routine = True if command_action == COMMAND_ROUTINE else False

  def __str__(self):
    return '<FIREFLY COMMAND - DEVICE: %s | SOURCE: %s | COMMAND: %s >' % (self.device, self.source, self.command)

  def export(self) -> dict:
    """
    Exports the command into a dict.

    This dict can be exported to a json file, then read and create a command from it. This is designed to be used for
    routines and the ability to export dynamically created routines to a json file to support a reboot of the system.

    Example:
      c = my_command.export()
      ...
        { write c to json file}
      ...

      Later

      ...
        { read from json file }
      ...

      my_command = Command(**c)
      firefly.send_command(my_command)


    Returns:
      (dict): Exported command data
    """
    export_data = {
      'device':         self.device,
      'source':         self.source,
      'command':        self.command,
      'command_action': self._command_action,
      'force':          self._force
    }
    export_data.update(self.args)
    return export_data

  @property
  def args(self):
    return self._args

  @property
  def device(self):
    return self._device

  @property
  def simple_command(self):
    return self._simple_command

  @property
  def command(self):
    return self._command

  @property
  def notify(self):
    return self._is_notify

  @property
  def speech(self):
    return self._is_speech


class Request(Event):
  def __init__(self, device, source: str, request, **kwargs):
    Event.__init__(self, source, EVENT_TYPE_REQUEST)
    self._device = aliases.get_device_id(device)
    self._request = request
    self._args = kwargs

  def __str__(self):
    return '<FIREFLY REQUEST - DEVICE: %s | SOURCE: %s | REQUEST: %s >' % (self.device, self.source, self.request)

  @property
  def request(self):
    return self._request

  @property
  def args(self):
    return self._args

  @property
  def device(self):
    return self._device