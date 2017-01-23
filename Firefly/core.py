import asyncio
import json
from typing import Any

from aiohttp import web

from Firefly.helpers.events import (Event, Command, Request)

from Firefly.helpers.subscribers import Subscriptions
from Firefly.helpers.alias import Alias
from Firefly import logging
from Firefly import aliases
from Firefly import scheduler
from Firefly.helpers.location import Location
from Firefly.const import (ACTION_ON, DEVICE_FILE, ACTION_TOGGLE, EVENT_ACTION_ANY, SOURCE_LOCATION, TYPE_DEVICE, EVENT_ACTION_LEVEL, TYPE_AUTOMATION, COMPONENT_MAP)
import importlib
from Firefly.automation import Trigger

import os

app = web.Application()


class Firefly(object):
  ''' Core running loop and scheduler of Firefly'''

  def __init__(self, settings):
    logging.Startup(self)
    logging.message('Initializing Firefly')
    self.settings = settings
    self.loop = asyncio.get_event_loop()
    self._subscriptions = Subscriptions()
    self.location = Location(self, "95110", ['HOME'])
    self._components = {}

    # TODO: POC of passing initial values. These values would comve from the export of the current state.
    # self.install_package('Firefly.components.test_device', alias='Test Device', initial_values={'_state': 'UNKNOWN'})
    #self.import_devices()

    for c in COMPONENT_MAP:
      self.import_devices(c['file'])


    # TODO: MOST OF WHATS BELOW IS FOR TESTING
    #self.install_package('Firefly.components.virtual_devices.switch', alias='Test Device', initial_values={'_state': 'UNKNOWN'})

    #for _, ff_id in self._devices.items():
    #  print(ff_id.export())

    # TODO: Test of routines
    #from Firefly.automation.routine import Routine
    #from Firefly.automation.triggers import Trigger
    #self._devices['test_routine'] = Routine(self, 'test_routine')
    #self._devices['test_routine'].add_trigger(Trigger('66fdff0a-1fa5-4234-91bc-465c72aafb23',EVENT_ACTION_ANY))
    #self._devices['test_routine'].add_trigger(Trigger('3b11cea9-a148-49d5-9467-bddb9f4ad937', EVENT_ACTION_LEVEL))
    #self._devices['test_routine'].add_trigger(Trigger('3b11cea9-a148-49d5-9467-bddb9f4ad937', EVENT_ACTION_ANY))
    #self._devices['test_routine'].add_trigger(Trigger(SOURCE_LOCATION, EVENT_ACTION_ANY))

    #self.install_package('Firefly.automation.routine', alias='Test Routines', ff_id='test_routine')
    #self.components['test_routine'].add_trigger(Trigger('66fdff0a-1fa5-4234-91bc-465c72aafb23',EVENT_ACTION_ANY))

    # Install service
    self.install_package('Firefly.services.darksky', alias='service Dark Sky')
    # Install openzwave
    #self.install_package('Firefly.services.zwave', alias='service zwave')

    # Start Notification service
    self.install_package('Firefly.services.notification')

    # Add Pushover
    




    # TODO: Remove this. This is a POC for scheduler.
    c = Command('Test Device', 'web_api', ACTION_TOGGLE)
    print(c.export())
    d_args = c.export()
    d = Command(**d_args)
    scheduler.runEveryH(1, self.send_command, command=d)

    # TODO: Leave In.
    scheduler.runEveryH(1, self.export_all_components)

  def start(self) -> None:
    """
    Start up Firefly.
    """
    # TODO: Import current state of components on boot.

    logging.message('Starting Firefly')

    try:
      web.run_app(app, host=self.settings.firefly_host, port=self.settings.firefly_port)
    except KeyboardInterrupt:
      pass
    finally:
      self.stop()

  def stop(self) -> None:
    ''' Shutdown firefly.

    Shutdown process should export the current state of all components so it can be imported on reboot and startup.
    '''
    # TODO: Export current state of components on shutdown

    logging.message('Stopping Firefly')
    self.export_all_components()

    # TODO: Remove this once exporting works
    for device in self.components:
      print(self.components[device].__dict__)

    self.loop.close()

  @asyncio.coroutine
  def add_task(self, task):
    logging.debug('Adding task to Firefly scheduler: %s' % str(task))
    future = asyncio.Future()
    r = yield from asyncio.ensure_future(task)
    future.set_result(r)
    return r

  def export_all_components(self) -> None:
    """
    Export current values to backup files to restore current config on reboot.
    """
    logging.message('Exporting current config.')
    for c in COMPONENT_MAP:
      self.export_components(c['file'], c['type'])
    aliases.export_aliases()

  def import_devices(self, config_file=DEVICE_FILE):
    logging.message('Importing components from config file.')
    # TODO: Check for duplicate alias and or IDs.
    devices = {}
    with open(config_file) as file:
      devices = json.loads(file.read())

    for device in devices:
      self.install_package(device.get('package'), **device)

  def export_components(self, config_file: str, component_type: str, current_values: bool = True) -> None:
    """
    Export all components with config and optional current states to a config file.

    Args:
      config_file (str): Path to config file.
      current_values (bool): Include current values.
    """
    logging.message('Exporting component and states to config file. - %s' % component_type)
    components = []
    for _, device in self.components.items():
      if device.type == component_type:
        components.append(device.export(current_values=current_values))

    with open(config_file, 'w') as file:
      json.dump(components, file, indent=4, sort_keys=True)

  def install_package(self, module: str, **kwargs):
    """
    Installs a package from the module. The package must support the Setup(firefly, **kwargs) function.

    The setup function can (and should) add the ff_id (if a ff_id) to the firefly._devices dict.

    Args:
      module (str): path to module being imported
      **kwargs (): If possible supply alias and/or device_id
    """
    logging.message('Installing module from %s %s' % (module, str(kwargs)))
    package = importlib.import_module(module)
    if kwargs.get('package'):
      kwargs.pop('package')
    return package.Setup(self, module, **kwargs)

  @asyncio.coroutine
  def send_event(self, event: Event) -> None:
    yield from self.add_task(self._send_event(event))

  @asyncio.coroutine
  def _send_event(self, event: Event) -> None:
    send_to = self._subscriptions.get_subscribers(event.source, event_action=event.event_action)
    logging.debug('Sending Event: %s -> %s' % (event, str(send_to)))
    for s in send_to:
      yield from self.__send_event(s, event)

  @asyncio.coroutine
  def __send_event(self, send_to: str, event: Event) -> None:
    r = yield from self.components[send_to].event(event)
    return r

  @asyncio.coroutine
  def send_request(self, request: Request) -> Any:
    """
    Send a request to a ff_id or app.

    Args:
      request (Request): Request to be sent

    Returns:
      Requested data.
    """
    result = yield from self.add_task(self._send_request(request))
    #result =  yield from self.loop.create_task(self._send_request(request))
    return result

  @asyncio.coroutine
  def _send_request(self, request: Request) -> Any:
    if request.ff_id not in self.components.keys():
      return False
    return self.components[request.ff_id].request(request)

  @asyncio.coroutine
  def send_command(self, command: Command) -> bool:
    """
    Send a command to a ff_id or app.

    Args:
      command (Command):

    Returns:
      (bool): Command successfully sent.
    """
    result = yield from self.add_task(self._send_command(command))
    return result

  @asyncio.coroutine
  def _send_command(self, command: Command) -> bool:
    if command.device not in self.components.keys():
      return False
    return self.components[command.device].command(command)

  def add_route(self, route, method, handler):
    app.router.add_route(method, route, handler)

  def add_get(self, route, handler, *args):
    app.router.add_get(route, handler)

  @property
  def components(self):
    return self._components

  @property
  def subscriptions(self):
    return self._subscriptions


def myTestFunction():
  print('Running Test Function')