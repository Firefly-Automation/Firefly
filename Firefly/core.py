import asyncio
import configparser
import importlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from aiohttp import web

from Firefly import aliases, logging, scheduler
from Firefly.const import COMPONENT_MAP, DEVICE_FILE, SERVICE_CONFIG_FILE, TIME
from Firefly.helpers.events import (Event, Request)
from Firefly.helpers.location import Location
from Firefly.helpers.room import Rooms
from Firefly.helpers.subscribers import Subscriptions

app = web.Application()


class Firefly(object):
  ''' Core running loop and scheduler of Firefly'''

  def __init__(self, settings):
    # TODO: Most of this should be in startup not init.
    logging.Startup(self)
    logging.message('Initializing Firefly')
    self._components = {}
    self.settings = settings
    self.loop = asyncio.get_event_loop()

    self.executor = ThreadPoolExecutor(max_workers=10)
    self.loop.set_default_executor(self.executor)

    self._subscriptions = Subscriptions()

    self.location = Location(self, self.settings.postal_code, self.settings.modes)


    # Start Notification service
    self.install_package('Firefly.services.notification', alias='service notification')

    # self.install_package('Firefly.components.notification.pushover', alias='Pushover', api_key='KEY', user_key='KEY')

    for c in COMPONENT_MAP:
      self.import_devices(c['file'])

    # TODO: Building rooms will have to happen whenever a devices is added
    self._rooms = Rooms(self)
    self._rooms.build_rooms()

    # TODO: MOST OF WHATS BELOW IS FOR TESTING
    # self.install_package('Firefly.components.virtual_devices.switch', alias='Test Device', initial_values={
    # '_state': 'UNKNOWN'})

    # self.install_package('Firefly.components.virtual_devices.presence', alias='Ariel Presence')
    # self.install_package('Firefly.components.virtual_devices.presence', alias='Zach Presence')

    # for _, ff_id in self._devices.items():
    #  print(ff_id.export())

    # TODO: Test of routines
    # from Firefly.automation.routine import Routine
    # from Firefly.automation.triggers import Trigger
    # self._devices['test_routine'] = Routine(self, 'test_routine')
    # self._devices['test_routine'].add_trigger(Trigger('66fdff0a-1fa5-4234-91bc-465c72aafb23',EVENT_ACTION_ANY))
    # self._devices['test_routine'].add_trigger(Trigger('3b11cea9-a148-49d5-9467-bddb9f4ad937', EVENT_ACTION_LEVEL))
    # self._devices['test_routine'].add_trigger(Trigger('3b11cea9-a148-49d5-9467-bddb9f4ad937', EVENT_ACTION_ANY))
    # self._devices['test_routine'].add_trigger(Trigger(SOURCE_LOCATION, EVENT_ACTION_ANY))

    # self.install_package('Firefly.automation.routine', alias='Test Routines', ff_id='test_routine')
    # self.components['test_routine'].add_trigger(Trigger('66fdff0a-1fa5-4234-91bc-465c72aafb23',EVENT_ACTION_ANY))

    logging.error(code='FF.COR.INI.001')  # this is a test error message
    logging.notify('Firefly is starting up')

    self.install_services()

    # TODO: Leave In.
    scheduler.runEveryH(1, self.export_all_components)

  def install_services(self) -> None:
    logging.notify('Installing Services')
    config = configparser.ConfigParser()
    config.read(SERVICE_CONFIG_FILE)
    services = config.sections()

    for service in services:
      package = config.get(service, 'package')
      alias = ('service_%s' % service).lower()
      enabled = config.getboolean(service, 'enable', fallback=False)
      if not enabled:
        continue

      try:
        self.install_package(package, alias=alias)
      except Exception as e:
        logging.error(code='FF.COR.INS.001', args=(service, e))  # error installing package %s: %s
        logging.notify('Error installing package %s: %s' % (service, e))


  def start(self) -> None:
    """
    Start up Firefly.
    """
    # TODO: Import current state of components on boot.
    try:
      web.run_app(app, host=self.settings.firefly_host, port=self.settings.firefly_port)
    except KeyboardInterrupt:
      self.export_all_components()
    finally:
      self.stop()

  def stop(self) -> None:
    ''' Shutdown firefly.

    Shutdown process should export the current state of all components so it can be imported on reboot and startup.
    '''
    # TODO: Export current state of components on shutdown
    logging.message('Stopping Firefly')

    # TODO: export automation.
    self.export_all_components()

    try:
      logging.message('Stopping zwave service')
      self.components['service_zwave'].stop()
    except:
      pass

    self.loop.close()

  @asyncio.coroutine
  def add_task(self, task):
    logging.debug('Adding task to Firefly scheduler: %s' % str(task))
    future = asyncio.Future()
    r = yield from asyncio.ensure_future(task)
    future.set_result(r)
    return r

  def delete_device(self, ff_id):
    self.components.pop(ff_id)
    if self.components.get('service_firebase'):
      self.components['service_firebase'].refresh_all()

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

  def send_firebase(self, event):
    if self.components.get('service_firebase'):
      self.components['service_firebase'].push(event.source, event.event_action)

  @asyncio.coroutine
  def async_send_event(self, event):
    logging.info('Received event: %s' % event)
    s = True
    fut = asyncio.Future(loop=self.loop)
    send_to = self._subscriptions.get_subscribers(event.source, event_action=event.event_action)
    for s in send_to:
      s &= yield from self._send_event(event, s, fut)
    self.send_firebase(event)
    return s

  def send_event(self, event: Event) -> Any:
    logging.info('Received event: %s' % event)
    fut = asyncio.Future(loop=self.loop)
    send_to = self._subscriptions.get_subscribers(event.source, event_action=event.event_action)
    for s in send_to:
      # asyncio.ensure_future(self._send_event(event, s, fut), loop=self.loop)
      self.components[s].event(event)
      # self.loop.run_in_executor(None,self.components[s].event, event)
    self.send_firebase(event)
    return True

  @asyncio.coroutine
  def _send_event(self, event, ff_id, fut):
    result = self.components[ff_id].event(event)
    # fut.set_result(result)
    return result

  @asyncio.coroutine
  def async_send_request(self, request):
    fut = asyncio.Future(loop=self.loop)
    r = yield from self._send_request(request, fut)
    return r

  def send_request(self, request: Request) -> Any:
    fut = asyncio.Future(loop=self.loop)
    result = asyncio.ensure_future(self._send_request(request, fut), loop=self.loop)
    return result

  @asyncio.coroutine
  def _send_request(self, request, fut):
    result = self.components[request.ff_id].request(request)
    fut.set_result(result)
    return result

  def send_command(self, command):
    fut = asyncio.Future(loop=self.loop)
    # result = asyncio.ensure_future(self._send_command(command, fut), loop=self.loop)
    if command.device not in self.components:
      return False
    try:
      self.loop.run_in_executor(None, self.components[command.device].command, command)
    except Exception as e:
      logging.error(code='FF.COR.SEN.001') #unknown error sending command
      logging.error(e)
    # TODO: Figure out how to wait for result
    return True

  @asyncio.coroutine
  def async_send_command(self, command):
    fut = asyncio.Future(loop=self.loop)
    result = yield from asyncio.ensure_future(self._send_command(command, fut), loop=self.loop)
    return result

  @asyncio.coroutine
  def _send_command(self, command, fut):
    if command.device in self.components:
      result = self.components[command.device].command(command)
      fut.set_result(result)
      return result
    logging.error(code='FF.COR._SE.001', args=(command.device))  # device not found %s
    return None

  def add_route(self, route, method, handler):
    app.router.add_route(method, route, handler)

  def add_get(self, route, handler, *args):
    app.router.add_get(route, handler)

  def get_device_states(self, devices: set) -> dict:
    current_state = {}
    if TIME in devices:
      devices.remove(TIME)
    if 'location' in devices:
      devices.remove('location')
    for device in devices:
      current_state[device] = self.components[device].get_all_request_values()
    return current_state

  @property
  def components(self):
    return self._components

  @property
  def subscriptions(self):
    return self._subscriptions
