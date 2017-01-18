from FIrefly import logging
from Firefly.helpers.events import Event, Command, Request

class Service(object):
  def __init__(self, firefly, service_id, title, author, package, commands, requests):
    self._firefly = firefly
    self._title = title
    self._author = author
    self._package = package
    self._commands = commands
    self._requests = requests
    self._command_mapping = {}
    self._request_mapping = {}

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

  def command(self, command: Command) -> bool:
    """
    Function that is called to send a command to a ff_id.
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
      broadcast = Event(self.id, EVENT_TYPE_BROADCAST, event_action=event_action)
      yield from self._firefly.send_event(broadcast)
      logging.info(broadcast)
      # TODO: END
      return True
    return False

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