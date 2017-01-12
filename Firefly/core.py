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
from Firefly.const import (ACTION_ON, DEVICE_FILE)

import importlib

import os

app = web.Application()



class Firefly(object):
  ''' Core running loop and scheduler of Firefly'''
  def __init__(self, settings):
    logging.message('Initializing Firefly')
    self.settings = settings
    self.loop = asyncio.get_event_loop()
    self.subscriptions = Subscriptions()
    self.location = Location(self, "95110", ['HOME'])
    self._devices = {}

    # TODO: POC of passing initial values. These values would comve from the export of the current state.
    #self.install_package('Firefly.devices.test_device', alias='Test Device', initial_values={'_state': 'UNKNOWN'})
    self.import_devices()

    for _, device in self._devices.items():
      print(device.export())


    # TODO: Remove this. This is a POC for scheduler.
    c = Command('Test Device', 'web_api', ACTION_ON)
    print(c.export())
    d_args = c.export()
    d = Command(**d_args)
    scheduler.runEveryS(15, self.send_command, command=d)


    # TODO: Leave In.
    scheduler.runEveryM(10, self.export_current_values)



  def start(self) -> None:
    ''' Start up Firefly.
    '''
    # TODO: Import current state of devices on boot.

    logging.message('Starting Firefly')

    try:
      web.run_app(app, host=self.settings.firefly_host, port=self.settings.firefly_port)
    except KeyboardInterrupt:
      pass
    finally:
      self.stop()


  def stop(self) -> None:
    ''' Shutdown firefly.

    Shutdown process should export the current state of all devices so it can be imported on reboot and startup.
    '''
    # TODO: Export current state of devices on shutdown

    logging.message('Stopping Firefly')
    self.export_current_values()

    # TODO: Remove this once exporting works
    for device in self.devices:
      print(self.devices[device].__dict__)

    self.loop.close()

  def add_task(self, task):
    logging.debug('Adding task to Firefly scheduler: %s' % str(task))
    future = asyncio.Future()
    r = yield from asyncio.ensure_future(task)
    future.set_result(r)
    return r

  def export_current_values(self) -> None:
    """
    Export current values to backup files to restore current config on reboot.
    """
    logging.message('Exporting current config.')
    self.export_devices()
    aliases.export_aliases()

  def import_devices(self, config_file=DEVICE_FILE):
    logging.message('Importing devices from config file.')
    devices = {}
    with open(config_file) as file:
      devices = json.loads(file.read())

    for device in devices:
      self.install_package(device.get('package'), **device)

  def export_devices(self, config_file: str=DEVICE_FILE, current_values: bool=True) -> None:
    """
    Export all devices with config and optional current states to a config file.

    Args:
      config_file (str): Path to config file.
      current_values (bool): Include current values.
    """
    logging.message('Exporting devices and states to config file.')
    devices = []
    for _, device in self.devices.items():
      devices.append(device.export(current_values))

    with open(config_file, 'w') as file:
      json.dump(devices, file, indent=4, sort_keys=True)

  def install_package(self, module: str, **kwargs):
    """
    Installs a package from the module. The package must support the Setup(firefly, **kwargs) function.

    The setup function can (and should) add the device (if a device) to the firefly._devices dict.

    Args:
      module (str): path to module being imported
      **kwargs (): If possible supply alias and/or device_id
    """
    logging.message('Installing module from %s %s' % (module, str(kwargs)))
    package = importlib.import_module(module)
    package.Setup(self, module, **kwargs)

  @asyncio.coroutine
  @asyncio.coroutine
  def send_event(self, event: Event) -> None:
    yield from self.add_task(self._send_event(event))

  @asyncio.coroutine
  def _send_event(self, event: Event) -> None:
    send_to = self.subscriptions.get_subscribers(event.source, event_action=event.event_action)
    logging.debug('Sending Event: %s -> %s' % (event, str(send_to)))
    for s in send_to:
      yield from self.__send_event(s, event)

  @asyncio.coroutine
  def __send_event(self, send_to: str, event: Event) -> None:
    self.devices[send_to].event(event)

  @asyncio.coroutine
  def send_request(self, request: Request) -> Any:
    """
    Send a request to a device or app.

    Args:
      request (Request): Request to be sent

    Returns:
      Requested data.
    """
    result = yield from self.add_task(self._send_request(request))
    return result

  @asyncio.coroutine
  def _send_request(self, request: Request) -> Any:
    if request.device not in self.devices.keys():
      return False
    return self.devices[request.device].request(request)


  @asyncio.coroutine
  def send_command(self, command: Command) -> bool:
    """
    Send a command to a device or app.

    Args:
      command (Command):

    Returns:
      (bool): Command successfully sent.
    """
    result = yield from self.add_task(self._send_command(command))
    return result

  @asyncio.coroutine
  def _send_command(self, command: Command) -> bool:
    if command.device not in self.devices.keys():
      return False
    return self.devices[command.device].command(command)


  def add_route(self, route, method, handler):
    app.router.add_route(method, route, handler)

  def add_get(self, route, handler, *args):
    app.router.add_get(route, handler)


  @property
  def devices(self):
    return self._devices


async def myTestFunction():
  print('Running Test Function')