# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-13 19:02:52
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-13 20:01:23

'''
IFTTT API

This API uses the IFTTT Maker channel to send commands to firefly

The URL will be the public facing address of your Serenity web interface:
https://PUBLIC_ADDRESS/API/ifttt?token=TOKEN_FOR_IFTTT

METHOD: POST
CONTENT TYPE: JSON

Samples of data:

[Change mode to TextField]
{"action":"mode", "mode":"{{TextField}}" }

[Turn off light]
{"action":"switch","device":"{{TextField}}", "state":"off"}
'''

import difflib
import json
import logging

from core import ffCommand
from core.database.device_db import getDeviceList
from core.database.routine_db import getRoutineList

def iftttHandler(p_request):
  action = p_request.get('action')
  if action == "mode":
    return ifttt_change_mode(p_request)
  if action == "switch":
    return ifttt_switch(p_request)
  return False

def ifttt_change_mode(request):
  routine_list = getRoutineList()
  mode = request.get('mode').lower()
  if mode is None:
    return False
  close_matches = difflib.get_close_matches(mode, routine_list)
  if len(close_matches) > 0:
    routine = close_matches[0]
    myCommand = ffCommand(routine, None, routine=True, source="IFTTT command", force=True)
    if myCommand.result:
      return True
  return False

def ifttt_switch(request):
  device_list = getDeviceList()
  device = request.get('device').lower()
  if device is None:
    return False
  state = request.get('state')
  close_matches = difflib.get_close_matches(device, device_list.keys())
  if len(close_matches) > 0:
    device = close_matches[0]
    myCommand = ffCommand(device_list.get(device), {'switch':state}, source="IFTTT command")
    if myCommand.result:
      return True
  return False