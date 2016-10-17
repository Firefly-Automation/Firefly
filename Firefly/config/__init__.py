# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:01:46
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-16 22:05:41

import configparser
import logging


class Modules(object):

  def __init__(self, config_file='config/modules.confg'):
    self._config = configparser.ConfigParser()
    self._config.read(config_file)

  def hasModule(self, module):
    return True if self.config.has_section(module) else False

  @property
  def config(self):
    return self._config


class Nest(object):

  def __init__(self, modules):
    logging.critical('Importing Nest Module')
    self._config = None
    self._username = None
    self._password = None
    self._enabled = False
    if modules.hasModule('nest'):
      self._config = modules.config['nest']
      self.readConfig()

  def readConfig(self):
    self._username = self.config.get('username')
    self._password = self.config.get('password')
    self._enabled = self.config.getboolean('enabled')

    if not self.username or not self.password:
      self._enabled = False
      logging.critical('NEST MODULE: DISABLED - ERROR WITH USERNAME OR PASSWORD')

  @property
  def config(self):
    return self._config

  @property
  def enabled(self):
    return self._enabled

  @property
  def username(self):
    return self._username

  @property
  def password(self):
    return self._password
