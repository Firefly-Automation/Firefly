# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-03 08:06:32
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-26 16:21:46
import logging

from core.models.command import Command as ffCommand
from core.models.device import Device
from core.models.event import Event as ffEvent
from core.utils.notify import Notification as ffNotify


import requests
import treq

import json



class Device(Device):
  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'Firefly Ecobee Controller',
      'type' : 'thermostat',
      'package' : 'ffEcobee',
      'module' : 'ffEcobee'
    }

    self.COMMANDS = {
      'getPin' : self.register_ecobee_get_pin,
      'getToken' : self.register_ecobee_get_token,
      'install' : self.install_ecobee,
      'update' : self.update,
      'setAway' : self.away,
      'setHome' : self.resume,
      'setMode' : self.set_mode
    }

    self.REQUESTS = {

    }

    self.VIEWS = {}

    args = args.get('args')
    self._api_key = args.get('api_key')
    self._api_url = 'https://api.lifx.com/v1/lights/'

    self._pin = None
    self._auth_code = None

    self._access_token = None
    self._refresh_token = None

    self._token_file = '.ecobee_tokens.json'

    name = args.get('name')
    super(Device,self).__init__(deviceID, name)

    self.install_ecobee()


  def register_ecobee_get_pin(self, args={}):
    url='https://api.ecobee.com/authorize?response_type=ecobeePin&client_id=' + str(self._api_key) + '&scope=smartWrite'
    response = requests.get(url).json()
    self._pin = response.get('ecobeePin')
    self._auth_code = response.get('code')
    ffNotify('all', 'Ecobee Auth Pin: ' + str(self._pin) + '. To finish installing ecobee, goto ecobee.com, login, from the menu on the right. Click Apps, Add App and enter Pin. After this is done you may preceed to the next step.')
    return str(self._pin)

  def register_ecobee_get_token(self, args={}):
    url = 'https://api.ecobee.com/token'
    data = {
      'grant_type': 'ecobeePin',
      'code' : str(self._auth_code),
      'client_id' : str(self._api_key)
    }
    response = requests.post(url, params=data)
    
    logging.critical(response.text)
    logging.critical(response.json())
    response = response.json()

    self._refresh_token = response.get('refresh_token')
    self._access_token = response.get('access_token')
    logging.critical(self._access_token)
    self.write_tokens_to_file()
    
  def refresh_token(self, args={}):
    url = 'https://api.ecobee.com/token'
    data = {
      'grant_type': 'refresh_token',
      'code' : str(self._refresh_token),
      'client_id' : str(self._api_key)
    }
    response = requests.post(url, params=data)
    
    logging.critical(response.text)
    logging.critical(response.json())
    response = response.json()

    self._refresh_token = response.get('refresh_token')
    self._access_token = response.get('access_token')
    logging.critical(self._access_token)
    self.write_tokens_to_file()


  def write_tokens_to_file(self):
    with open(self._token_file, 'w+') as token_file:
      tokens = {
        'refresh_token' : str(self._refresh_token),
        'access_token' : str(self._access_token)
      }
      json.dump(tokens, token_file)

  def read_tokens_from_file(self):
    try:
      with open(self._token_file, 'r') as token_file:
        tokens = json.load(token_file)
        self._refresh_token = tokens.get('refresh_token')
        self._access_token = tokens.get('access_token')
        return True
    except:
      return False

  def install_ecobee(self, args={}):
    if self.read_tokens_from_file():
      return True

    else:
      return False


  def away(self, args={}):
    self.refresh_token()
    data = {
      "selection": {
        "selectionType":"registered",
        "selectionMatch":""
      },
      "functions": [
        {
          "type":"setHold",
            "params":{
              "holdType":"indefinite",
              "holdClimateRef":"away"
            }
          }
        ]
      } 

    headers = {"Authorization": "Bearer " + str(self._access_token), 'Content-Type': 'application/json;charset=UTF-8' }
    params = {'format': 'json'}
    url = "https://api.ecobee.com/1/thermostat?format=json"

    r = requests.post(url, headers=headers, params=params, json=data)
    logging.critical(r.text)

    
  def resume(self, args={}):
    self.refresh_token()
    data = {
      "selection": {
        "selectionType":"registered",
        "selectionMatch":""
      },
      "functions": [
        {
          "type":"resumeProgram",
            "params":{
              "resumeAll":"true",
            }
          }
        ]
      } 

    headers = {"Authorization": "Bearer " + str(self._access_token), 'Content-Type': 'application/json;charset=UTF-8' }
    params = {'format': 'json'}
    url = "https://api.ecobee.com/1/thermostat?format=json"

    r = requests.post(url, headers=headers, params=params, json=data)
    logging.critical(r.text)

  def set_mode(self, args={}):
    mode = args.get('mode')
    self.refresh_token()
    data = {
      "selection": {
        "selectionType":"registered",
        "selectionMatch":""
      },
      "functions": [
        {
          "type":"setHold",
            "params":{
              "holdType":"holdHours",
              "holdClimateRef":str(mode),
              "holdHours":2
            }
          }
        ]
      } 

    headers = {"Authorization": "Bearer " + str(self._access_token), 'Content-Type': 'application/json;charset=UTF-8' }
    params = {'format': 'json'}
    url = "https://api.ecobee.com/1/thermostat?format=json"

    r = requests.post(url, headers=headers, params=params, json=data)
    logging.critical(r.text)
    
  def update(self, args={}):
      pass
    

