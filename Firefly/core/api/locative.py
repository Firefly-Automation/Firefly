# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-14 15:29:06
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-14 16:42:52

import logging

from core import ffCommand


class LocativeMessage(object):
  '''
  LocativeMessage holds the data sent by the LocativeGeofence app
  '''

  def __init__(self, request):
    self._request = request
    self._lat = self.getValue('latitude')
    self._lon = self.getValue('longitude')
    self._id = self.getValue('id')
    self._device = self.getValue('device')
    self._device_type = self.getValue('device_type')
    self._device_model = self.getValue('device_model')
    self._trigger = self.getValue('trigger')
    self._timestamp = self.getValue('timestamp')
    self._ff_device = self.getValue('ff_device')

  @property
  def ffDevice(self):
    return str(self._ff_device)

  @property
  def trigger(self):
    return self._trigger.lower()

  @property
  def presence(self):
    return True if self.trigger == 'enter' else False

  def getValue(self, value):
    return self._request.args.get(value)


def locativeHandler(request):
  '''
  locativeHandler takes a flask request and updates the
  presence of a device. It retuerns a LocativeMessage.

  The URL of the request has to be:
  https://PUBLIC_ADDRESS/API/locative?ff_device=FF_DEVICE_ID&token=LOCATIVE_TOKEN
  '''
  message = LocativeMessage(request)
  logging.debug('locative: got message from {} presence: {}'.format(message.ffDevice, message.presence))
  ffCommand(message.ffDevice,
            {'presence': message.presence},
            source='Locative Presence API')
  return message
