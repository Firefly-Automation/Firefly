#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:01:46
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-12-29 23:53:18

import ConfigParser
import logging


class ServiceConfig(object):
  '''This is the updated version'''

  def __init__(self, config_file='/opt/firefly_system/config/services.config'):
    self._config = ConfigParser.ConfigParser()
    self._config.read(config_file)

  def has_service(self, service):
    return True if self.config.has_section(service) else False

  def get_service_config(self, service):
    if not self.has_service(service):
      return False
    return dict(self._config.items(service))

  def get_boolean(self, service, item):
    if not self.has_service(service):
      return False
    return self._config.getboolean(service, item)

  def get_item(self, service, item):
    if not self.has_service(service):
      return False
    return self._config.get(service, item)

  @property
  def config(self):
    return self._config

class Modules(object):

  def __init__(self, config_file='/opt/firefly_system/config/services.config'):
    self._config = ConfigParser.ConfigParser()
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
