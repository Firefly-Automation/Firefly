from aiohttp import web
from aiohttp.web_reqrep import Request as webRequest
from datetime import datetime
import asyncio
import json

from Firefly import logging

from Firefly.const import (EVENT_ACTION_OFF, EVENT_ACTION_ON, TYPE_DEVICE, ACTION_OFF, ACTION_ON, STATE, API_INFO_REQUEST)
from Firefly.helpers.events import Command, Request

class FireflyCoreAPI:
  def __init__(self, firefly):
    self.firefly = firefly
    self.api_functions = [
      {'method': 'GET', 'path': '/', 'function': self.hello_world},
      {'method': 'GET', 'path': '/status', 'function': self.get_status},
      {'method': 'GET', 'path': '/stop', 'function': self.stop_firefly},
      {'method': 'GET', 'path': '/test', 'function': self.test},
      {'method': 'GET', 'path': '/api/rest/components', 'function': self.devices},
      {'method': 'GET', 'path': '/api/rest/ff_id/{ff_id}', 'function': self.device},
      {'method': 'GET', 'path': '/api/rest/ff_id/{ff_id}/action', 'function': self.action},
      {'method': 'GET', 'path': '/api/rest/ff_id/{ff_id}/sensors', 'function': self.sensors},
      {'method': 'GET', 'path': '/api/status/all_components', 'function': self.api_all_components},
      {'method': 'GET', 'path': '/api/status', 'function': self.api_status}
    ]

  async def hello_world(self, request):
    logging.debug('Hello World')
    return web.Response(text='Hello World')

  async def get_status(self, request):
    status = 'Running' if self.firefly.loop.is_running else 'Not Running'
    return web.Response(text=status)

  async def stop_firefly(self, request):
    self.firefly.stop()
    return web.Response(text='Stopped Firefly')

  async def devices(self, request):
    devices = []
    for ff_id, d in self.firefly.components.items():
      if d.type == TYPE_DEVICE:
        devices.append({
          'alias': d._alias,
          'title': d._title,
          'ff_id': ff_id,
          'rest_url': 'http://%s/api/rest/ff_id/%s' % (request.host, ff_id)
        })

    data = json.dumps(devices, indent=4, sort_keys=True)
    return web.Response(text=data, content_type='application/json')

  @asyncio.coroutine
  def action(self, request):
    ff_id = request.match_info['ff_id']
    if 'command' in request.GET:
      my_command = Command(ff_id,'web_api', **request.GET)
      yield from self.firefly.async_send_command(my_command)
      device_request = Request(ff_id, 'web_api', API_INFO_REQUEST)
      data = yield from self.firefly.async_send_request(device_request)
      data['rest_url'] = 'http://%s/api/rest/ff_id/%s' % (request.host, ff_id)
      return web.json_response(data)

    if 'request' in request.GET:
      my_request = Request(ff_id, 'web_api', **request.GET)
      result = yield from self.firefly.async_send_request(my_request)
      return web.Response(text=result, content_type='application/json')


  @asyncio.coroutine
  def device(self, request):
    ff_id = request.match_info['ff_id']
    device_request = Request(ff_id, 'web_api', API_INFO_REQUEST)
    data = yield from self.firefly.async_send_request(device_request)
    print('data :%s' % data)
    data['rest_url'] = 'http://%s/api/rest/ff_id/%s' % (request.host, ff_id)
    return web.json_response(data)


  @asyncio.coroutine
  def sensors(self, request):
    ff_id = request.match_info['ff_id']
    device_request = Request(ff_id, 'web_api', 'SENSORS', **request.GET)
    data = yield from self.firefly.async_send_request(device_request)
    return web.json_response(data)




  @asyncio.coroutine
  def test(self, request):
    command = Command(**{'command':'TOGGLE', 'ff_id':'66fdff0a-1fa5-4234-91bc-465c72aafb23', 'source':'testing'})
    yield from self.firefly.send_command(command)
    return web.Response(text=str(command))


  @asyncio.coroutine
  def get_component_view(self, ff_id, source):
    device_request = Request(ff_id, source, API_INFO_REQUEST)
    data = yield from self.firefly.async_send_request(device_request)
    return data

  @asyncio.coroutine
  def get_all_component_views(self, source, filter=None):
    if type(filter) is str:
      filter = [filter]
    views = []
    for ff_id, device in self.firefly.components.items():
      if device.type in filter or filter is None:
        data = yield from self.get_component_view(ff_id, source)
        views.append(data)
    return views


  @asyncio.coroutine
  def api_all_components(self, request):
    return web.Response(text='api_all_components')

  @asyncio.coroutine
  def api_status(self, request:webRequest):
    source = request.rel_url.query.get('source')
    print(source)
    source = 'web_api' if source is None else source
    status_data = {}
    status_data['devices'] = yield from self.get_all_component_views(source, filter=TYPE_DEVICE)
    now = self.firefly.location.now
    status_data['time'] = {'epoch':now.timestamp(), 'day':now.day, 'month':now.month, 'year':now.year, 'hour':now.hour, 'minute':now.minute, 'str':str(now)}
    status_data['is_dark'] = self.firefly.location.isDark
    status_data['mode'] = self.firefly.location.mode
    status_data['last_mode'] = self.firefly.location.lastMode

    data = json.dumps(status_data, indent=4, sort_keys=True)
    return web.Response(text=data, content_type='application/json')



  def setup_api(self):
    for function in self.api_functions:
      print(function)
      self.firefly.add_route(function.get('path'),function.get('method'), function.get('function'))
