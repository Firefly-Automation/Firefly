from Firefly import logging
from Firefly.helpers.events import Event, Command, Request
from Firefly.const import EVENT_TYPE_BROADCAST
from typing import Callable, Any
from Firefly.const import STATE

class Device(object):
  def __init__(self, firefly, device_id, title, author, package, commands, requests):
    self._firefly = firefly
    self._id = device_id
    self._title = title
    self._author = author
    self._package = package
    self._commands = commands
    self._requests = requests
    self._command_mapping = {}
    self._request_mapping = {}

  def __str__(self):
    return '< FIREFLY DEVICE - ID: %s | PACKAGE: %s >' % (self.id, self._package)

  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported device commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self._command_mapping[command] = function

  def add_request(self, request: str, function: Callable) -> None:
    """
    Adds a request to the list of supported device requests.

    Args:
      request (str): The string of the request
      function (Callable): The function to be executed.
    """
    self._request_mapping[request] = function

  def command(self, command: Command) -> bool:
    """
    Function that is called to send a command to a device.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    state_before = self.__dict__.copy()
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    if command.command in self.command_map.keys():
      event_action = self.command_map[command.command](**command.args)
      if not event_action:
        return True
      if state_before == self.__dict__:
        return True
      logging.info('Change detected: %s' % self)
      # TODO: If change detected then send broadcast event
      broadcast = Event(self.id, EVENT_TYPE_BROADCAST, event_action)
      logging.info(broadcast)
      # TODO: END
      return True
    return False

  def request(self, request: Request) -> Any:
    """
    Function to request data from the device. The returned data can be in any format. Common formats should be:
      str, int, dict

    Args:
      request (Request): Request object

    Returns:
      Requested Data

    """
    logging.debug('%s: Got Request %s' % (self.id, request))
    if request.request in self.request_map.keys():
      return self.request_map[request.request](**request.args)
    return None

  @property
  def id(self):
    return self._id

  @property
  def command_map(self):
    return self._command_mapping

  @property
  def request_map(self):
    return self._request_mapping
