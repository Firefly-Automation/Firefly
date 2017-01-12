from aiohttp import web
import asyncio

from Firefly import logging
from Firefly.core import myTestFunction

from Firefly.const import (STATE_OFF, STATE_ON, ACTION_OFF, ACTION_ON, STATE)
from Firefly.helpers.events import Command, Request

class FireflyCoreAPI:
  def __init__(self, firefly):
    self.firefly = firefly
    self.api_functions = [
      {'method': 'GET', 'path': '/', 'function': self.hello_world},
      {'method': 'GET', 'path': '/status', 'function': self.get_status},
      {'method': 'GET', 'path': '/stop', 'function': self.stop_firefly},
      {'method': 'GET', 'path': '/test/{action}', 'function': self.test},
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

  @asyncio.coroutine
  def test(self, request):
    action = request.match_info['action']
    if action == 'off':
      c = Command('Test Device', 'web_api', ACTION_OFF)
      yield from self.firefly.send_command(c)
      request = Request('Test Device', 'web_api', STATE)
      state = yield from self.firefly.send_request(request)
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
