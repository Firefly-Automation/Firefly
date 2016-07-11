# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-25 22:13:31
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-26 18:07:48

import logging
import requests
import xml.etree.ElementTree as etree

from core.models.device import Device

COMMANDS = {
  'POWER' : 1,
  'Number 0' : 2,
  'Number 1' : 3,
  'Number 2' : 4,
  'Number 3' : 5,
  'Number 4' : 6,
  'Number 5' : 7,
  'Number 6' : 8,
  'Number 7' : 9,
  'Number 8' : 10,
  'Number 9' : 11,
  'UP key among remote Controller\'s 4 direction keys' : 12,
  'DOWN key among remote Controller\'s 4 direction keys' : 13,
  'LEFT key among remote Controller\'s 4 direction keys' : 14,
  'RIGHT key among remote Controller\'s 4 direction keys' : 15,
  'OK' : 20,
  'Home menu' : 21,
  'Menu key (same with Home menu key)' : 22,
  'Previous key (Back)' : 23,
  'Volume up' : 24,
  'Volume down' : 25,
  'Mute (toggle)' : 26,
  'Channel UP (+)' : 27,
  'Channel DOWN (-)' : 28,
  'Blue key of data broadcast' : 29,
  'Green key of data broadcast' : 30,
  'Red key of data broadcast' : 31,
  'Yellow key of data broadcast' : 32,
  'Play' : 33,
  'Pause' : 34,
  'Stop' : 35,
  'Fast forward (FF)' : 36,
  'Rewind (REW)' : 37,
  'Skip Forward' : 38,
  'Skip Backward' : 39,
  'Record' : 40,
  'Recording list' : 41,
  'Repeat' : 42,
  'Live TV' : 43,
  'EPG' : 44,
  'Current program information' : 45,
  'Aspect ratio' : 46,
  'External input' : 47,
  'PIP secondary video' : 48,
  'Show / Change subtitle' : 49,
  'Program list' : 50,
  'Tele Text' : 51,
  'Mark' : 52,
  '3D Video' : 400,
  '3D L/R' : 401,
  'Dash (-)' : 402,
  'Previous channel (Flash back)' : 403,
  'Favorite channel' : 404,
  'Quick menu' : 405,
  'Text Option' : 406,
  'Audio Description' : 407,
  'NetCast key (same with Home menu)' : 408,
  'Energy saving' : 409,
  'A/V mode' : 410,
  'SIMPLINK' : 411,
  'Exit' : 412,
  'Reservation programs list' : 413,
  'PIP channel UP' : 414,
  'PIP channel DOWN' : 415,
  'Switching between primary/secondary video' : 416,
  'My Apps' : 417
}

class Device(Device):

  def __init__(self, deviceID, args={}):
    self.METADATA = {
      'title' : 'LG TV Control',
      'author' : 'Zachary Priddy',
      'type' : 'controller',
      'module' : 'ffLgControl'
    }
    
    self.COMMANDS = {
      'pin' : self.showPin,
      'off' : self.setOff,
      'command' : self.sendCommand,
      'switch' : self.setOff
    }

    self.REQUESTS = {
      'status' : self.get_status
    }

    self.VIEWS = {
      'display' : True,
      'name' : args.get('args').get('name'),
      'id' : deviceID,
      'type' : 'Entertainment',
      'dash_view' : {
        'request' : 'status',
        'type' : 'button', 
        'button' : {
          "true" : {
            'click' : 'false',
            'color' : 'orange lighten-1',
            'command' : {'cmd':'POWER'},
            'text' : 'Off'
          },
          "false" : {
            'click' : 'false',
            'color' : 'orange lighten-1',
            'command' : {'cmd':'POWER'},
            'default' : True,
            'text' : 'Off'
          }
        }
      }
    }

    ###########################
    # SET VARS
    ###########################
    args = args.get('args')
    self._ip = args.get('ip')
    self._port = args.get('port')
    self._pin = args.get('pin')

    ###########################
    # DONT CHANGE
    ###########################
    name = args.get('name')
    super(Device,self).__init__(deviceID, name)
    ###########################
    ###########################

#############################################################

  def setOff(self, args={}):
    self.sendCommand(args={'command':{'cmd':'POWER'}})

  def showPin(self, args={}):
    pass

  def sendCommand(self, args={}):
    try:
      args=args.command
      logging.critical(args)
      if args.get('code'):
        command = args.get('code')
      else:
        command = COMMANDS.get(args.get('cmd'))
        #TODO fix temp fix of default to power
        if command is None:
            command = 1
        logging.critical('Command: ' + str(command))
      if command is None:
        return -1

      headers = {"Content-Type": "application/atom+xml"}

      cmdText = "<!--?xml version=\"1.0\" encoding=\"utf-8\"?--><command>" \
              + "<name>HandleKeyInput</name><value>" \
              + str(command) \
              + "</value></command>"

      url = 'http://' + str(self._ip) + ':' + str(self._port) + '/roap/api/command'

      if not self.get_session():
        return -1
      r = requests.post(url, data=cmdText, headers=headers)
      if r.status_code == 200:
        return True
      else:
        return False
    except:
      return -1

  def get_session(self, args={}):
    logging.critical('Get Session')
    headers = {"Content-Type": "application/atom+xml"}
    url = 'http://' + str(self._ip) + ':' + str(self._port) + '/roap/api/auth'
    cmdText = "<!--?xml version=\"1.0\" encoding=\"utf-8\"?--><auth><type>AuthReq</type><value>" \
          + str(self._pin) + "</value></auth>"

    logging.critical(url)
    logging.critical(cmdText)
    r = requests.post(url, data=cmdText, headers=headers)
    
    logging.critical(r.status_code)
    if r.status_code != 200:
      return False
    logging.critical(r.text)
    tree = etree.XML(r.text)
    session = tree.find('session').text
    logging.critical(session)
    if session == "Unauthorized":
      logging.critical('CANT GET LG SESSION')
      return False
    return session

  def get_status(self, args={}):
    pass