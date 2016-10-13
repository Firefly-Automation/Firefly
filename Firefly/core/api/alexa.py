# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-13 00:36:33
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-13 00:42:08

import difflib
import json

from core import ffCommand, getDeviceList, getRoutineList

def alexaHandler(p_request):
  p_request = json.loads(p_request)
  request = p_request.get('request')
  r_type = None
  if request is not None:
    r_type = request.get('type')
  
  if r_type == "LaunchRequest":
    return launch_request(request)
  elif r_type == "IntentRequest":
    return intent_request(request)
  else:
    return launch_request(request)
  
def launch_request(request):
  output_speech = "Welcome to Firefly Smart Home. Please say a command"
  output_type = "PlainText"
  
  card_type = "Simple"
  card_title = "Firefly Smart Home"
  card_content = "Welcome to Firefly Smart Home. You can say commands such as: Alexa, tell firefly to say good night. Alexa, tell firefly to set home to away"
  
  response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':False}
  
  return response
  
  
def intent_request(request):
  intent = request.get('intent')
  if intent is not None:
    intent_name = intent.get('name')
    logging.critical(intent_name)
    if intent_name == 'ChangeMode':
      return echo_change_mode(intent)
    if intent_name == 'Switch':
      return echo_switch(intent)
    if intent_name == 'Dimmer':
      return echo_dimmer(intent)

  return launch_request(request)

def echo_change_mode(intent):
  routine_list = getRoutineList()
  mode = intent.get('slots').get('mode').get('value').lower()
  close_matches = difflib.get_close_matches(mode, routine_list)
  if len(close_matches) < 1:
    get_routines_list()
    close_matches = difflib.get_close_matches(mode, routine_list)
  if len(close_matches) > 0:
    routine = close_matches[0]
    myCommand = ffCommand(routine, None, routine=True, source="Echo command", force=True)
    if myCommand.result:
      return make_response("Changed mode to " + str(routine), "Changed mode to " + str(routine))
  
  return make_response("Error changing mode to " + str(mode), "Error changing mode to " + str(mode), card_title="Firefly Smart Home Error")

def echo_switch(intent):
  device_list = getDeviceList()
  device = intent.get('slots').get('device').get('value').lower()
  state = intent.get('slots').get('state').get('value')
  close_matches = difflib.get_close_matches(device, device_list.keys())
  logging.critical(device_list)
  logging.critical(close_matches)
  if len(close_matches) < 1:
    get_device_list()
    close_matches = difflib.get_close_matches(device, device_list.keys())
  if len(close_matches) > 0:
    device = close_matches[0]
    myCommand = ffCommand(device_list.get(device), {'switch':state})
    if myCommand.result:
      return make_response("Turned " + str(device) + " " + str(state), "Turned " + str(device) + " " +  str(state))

  return make_response("Error finding device " + str(device), "Error finding device " + str(device), card_title="Firefly Smart Home Error")

def echo_dimmer(intent):
  device_list = getDeviceList()
  device = intent.get('slots').get('device').get('value').lower()
  level = int(intent.get('slots').get('level').get('value'))
  close_matches = difflib.get_close_matches(device, device_list.keys())
  if len(close_matches) < 1:
    get_device_list()
    close_matches = difflib.get_close_matches(device, device_list.keys())
  if len(close_matches) > 0:
    device = close_matches[0]
    myCommand = ffCommand(device_list.get(device), {'setLight' : {'level':level}})
    if myCommand.result:
      return make_response("Set " + str(device) + " to " + str(level) + " percent.", "Set " + str(device) + " to " + str(level) + "percent.")

  return make_response("Error finding device " + str(device), "Error finding device " + str(device), card_title="Firefly Smart Home Error")
  
def make_response(output_speech, card_content, output_type="PlainText", card_title="Firefly Smart Home", card_type="Simple", end_session=True):
  response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':end_session}
  return response
