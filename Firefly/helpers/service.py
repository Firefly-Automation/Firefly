import asyncio

from Firefly import logging
from Firefly.helpers.events import Event, Command, Request
from typing import Callable, Any
from Firefly.const import TYPE_SERVICE, EVENT_TYPE_BROADCAST

class Service(object):
  def __init__(self, firefly, service_id, package, title, author, commands, requests):
    self._firefly = firefly
    self._title = title
    self._author = author
    self._package = package
    self._commands = commands
    self._requests = requests
    self._command_mapping = {}
    self._request_mapping = {}

    # service_id should be set by the service and should be something like service_<NAME>
    self._service_id = service_id

    # TODO: Alias mapping for service.


  # TODO: The following were copied from Device. Verify They work right
  def add_command(self, command: str, function: Callable) -> None:
    """
    Adds a command to the list of supported ff_id commands.

    Args:
      command (str): The string of the command
      function (Callable): The function to be executed.
    """
    self._command_mapping[command] = function

  def add_request(self, request: str, function: Callable) -> None:
    """
    Adds a request to the list of supported ff_id requests.

    Args:
      request (str): The string of the request
      function (Callable): The function to be executed.
    """
    self._request_mapping[request] = function


  def command(self, command: Command, **kwargs) -> bool:
    """
    Function that is called to send a command to a ff_id.
    Args:
      command (Command): The command to be sent in a Command object

    Returns:
      (bool): Command successful.
    """
    #state_before = self.__dict__.copy()
    logging.debug('%s: Got Command: %s' % (self.id, command.command))
    if command.command in self.command_map.keys():
      event_action =  self.command_map[command.command](**command.args)
      return event_action


  def request(self, request: Request) -> Any:
    """
    Function to request data from the ff_id. The returned data can be in any format. Common formats should be:
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

  def event(self, event: Event) -> None:
    logging.error('Devices currently dont support events')

  @property
  def id(self):
    return self._service_id

  @property
  def command_map(self):
    return self._command_mapping

  @property
  def request_map(self):
    return self._request_mapping

  @property
  def type(self):
    return TYPE_SERVICE