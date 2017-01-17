from aiohttp import web
import asyncio
import json

from Firefly import logging
from Firefly.core import myTestFunction

from Firefly.const import (STATE_OFF, STATE_ON, TYPE_DEVICE, ACTION_OFF, ACTION_ON, STATE, API_INFO_REQUEST)
from Firefly.helpers.events import Command, Request

class FireflyCoreAPI:
  def __init__(self, firefly):
    self.firefly = firefly
    self.api_functions = [
      {'method': 'GET', 'path': '/', 'function': self.hello_world},
      {'method': 'GET', 'path': '/status', 'function': self.get_status},
      {'method': 'GET', 'path': '/stop', 'function': self.stop_firefly},
      {'method': 'GET', 'path': '/test/{action}', 'function': self.test},
      {'method': 'GET', 'path': '/api/rest/devices', 'function': self.devices},
      {'method': 'GET', 'path': '/api/rest/device/{ff_id}', 'function': self.device},
      {'method': 'GET', 'path': '/api/rest/device/{ff_id}/action', 'function': self.action}
    ]

  async def hello_world(self, request):
    logging.debug('Hello World')
    self.firefly.add_task(myTestFunction())
    return web.Response(text='Hello World')

  async def get_status(self, request):
    status = 'Running' if self.firefly.loop.is_running else 'Not Running'
    return web.Response(text=status)

  async def stop_firefly(self, request):
    self.firefly.stop()
    return web.Response(text='Stopped Firefly')

  async def devices(self, request):
    devices = []
    for ff_id, d in self.firefly.devices.items():
      if d.type == TYPE_DEVICE:
        devices.append({
          'alias': d._alias,
          'title': d._title,
          'ff_id': ff_id,
          'rest_url': 'http://%s/api/rest/device/%s' % (request.host, ff_id)
        })

    data = json.dumps(devices, indent=4, sort_keys=True)
    return web.Response(text=data, content_type='application/json')

  @asyncio.coroutine
  def action(self, request):
    ff_id = request.match_info['ff_id']
    if 'command' in request.GET:
      my_command = Command(ff_id,'web_api', **request.GET)
      yield from self.firefly.send_command(my_command)
      device_request = Request(ff_id, 'web_api', API_INFO_REQUEST)
      data = yield from self.firefly.send_request(device_request)
      data['rest_url'] = 'http://%s/api/rest/device/%s' % (request.host, ff_id)
      return web.json_response(data)

    if 'request' in request.GET:
      my_request = Request(ff_id, 'web_api', **request.GET)
      result = yield from self.firefly._send_request(my_request)
      return web.Response(text=result, content_type='application/json')


  @asyncio.coroutine
  def device(self, request):
    ff_id = request.match_info['ff_id']
    device_request = Request(ff_id, 'web_api', API_INFO_REQUEST)
    data = yield from self.firefly.send_request(device_request)
    data['rest_url'] = 'http://%s/api/rest/device/%s' % (request.host, ff_id)
    return web.json_response(data)


  @asyncio.coroutine
  def test(self, request):
    action = request.match_info['action']
    if action == 'off':
      c = Command('Test Device', 'web_api', ACTION_OFF)
      yield from self.firefly.send_command(c)
      request = Request('Test Device', 'web_api', STATE)
      state =  yield from self.firefly.send_request(request)
      r = web.Response(text=str(state))
      return r
    if action == 'on':
      c = Command('Test Device', 'web_api', ACTION_ON)
      yield from self.firefly.send_command(c)
      request = Request('Test Device', 'web_api', STATE)
      state = yield from self.firefly.send_request(request)
      r = web.Response(text=str(state))
      return r

    request = Request('Test Device', 'web_api', STATE)
    state = yield from self.firefly.send_request(request)
    return web.Response(text=str(state))



  def setup_api(self):
    for function in self.api_functions:
      print(function)
      self.firefly.add_route(function.get('path'),function.get('method'), function.get('function'))
