# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-19 21:57:10
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-09 22:40:00

import pychromecast
import requests
from core import deviceDB, ffCommand
from config import ServiceConfig
import logging

config = ServiceConfig()

class Notification(object):
  def __init__(self, deviceID, message, priority=0, cast=False):
    self._deviceID = deviceID
    self._message = message
    self._priority = priority

    if cast:
      if not config.get_boolean('SPEECH','enable'):
        return False
      return self.send_cast(self._deviceID)

    if self._deviceID.lower() == 'all':
      return self.send_all()
    else:
      return self.send()

  def send_cast(self, device):
    logging.error('***************************************')
    logging.error(device)
    polly_server = config.get_item('SPEECH', 'polly_server')
    media_url = requests.post(polly_server, json={'speech': self._message}).text
    chromecasts = pychromecast.get_chromecasts()
    logging.error(media_url)
    logging.error(chromecasts)
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == device)
    cast.set_volume(.5)
    mc = cast.media_controller
    mc.play_media(media_url, 'audio/mp3')

  def send_all(self):
    for device in deviceDB.find({"config.subType":"notification"}):
      dID = device.get('id')
      ffCommand(str(dID), {'notify': {'message' :self._message}})
    if config.get_boolean('SPEECH','enable'):
      self.send_cast(config.get_item('SPEECH','default_device'))
    return True


  def send(self):
    return ffCommand(self._deviceID, {'notify': {'message' :self._message}})
