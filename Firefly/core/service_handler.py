"""
This is the handler file for installing, activating and updating services. This should only ever be called from core.

"""
import json
from os.path import isfile, join
from typing import Dict
from Firefly import logging
from Firefly.core.const import SERVICE_PACKAGE_FILE, SERVICE_CONFIG_DIR


"""
  ServiceConfig is the object that holds all the config values.
  Services should will receive a ServicePackage object (sp) 
  
  if not sp.enabled:
    return False
    
  self.service_package = sp
  try:
    self.config = sp.get_config()
  except ValueError:
    return False
  
  ...Install Service...  
"""


class ServiceConfig(object):
  def __init__(self, config_file, enabled):
    self.enabled = enabled
    self._config_file = config_file

  def set_item(self, item, value):
    setattr(self, item, value)

  def json(self):
    json_output = self.__dict__.copy()
    json_output.pop('_config_file')
    return json_output

  def save(self):
    """ Save config to file

    Returns: True if successful, false if failed.

    """
    try:
      with open(self._config_file, 'w+') as config_file:
        json.dump(self.json(), config_file, indent=4, sort_keys=True)
        return True
    except Exception as e:
      logging.error('error writing config to file: %s' % e)
      return False

  def reload(self):
    """ Reloads the config from the file.

    Returns: True if successful, False if failed.

    """
    try:
      new_config = read_config_file(self._config_file)
      for item, value in new_config.items():
        setattr(self, item, value)
      return True
    except Exception as e:
      logging.error('error reloading file: %s', e)
    return False


class ServiceParam(object):
  def __init__(self, context='', default=None, type='', self_init=False, default_init=False, **kwargs):
    self.context = context
    self.default = default
    self.type = type
    self.self_init = self_init
    self.default_init = default_init


def read_config_file(filename):
  if not isfile(filename):
    raise FileNotFoundError
  with open(filename, 'rb') as config_file:
    config = json.load(config_file)
    return config

def raise_value_error(value, missing_okay=False):
  if value is None and not missing_okay:
    raise ValueError
  return value


class ServicePackage(object):
  def __init__(self, config={}, defaults={}, description='', ff_id='', name='', package='', required={}, enable_default=False, **kwargs):
    self.config = {}
    for config_item, config_path in config.items():
      self.config[config_item] = join(SERVICE_CONFIG_DIR, config_path)
    self.description = description
    self.ff_id = ff_id
    self.name = name
    self.package = package
    self.enabled = enable_default
    self.required: Dict[str, ServiceParam] = {}
    self.defaults: Dict[str, ServiceParam] = {}
    self.installed = False

    for param_name, param in required.items():
      self.required[param_name] = ServiceParam(**param)

    for param_name, param in defaults.items():
      self.defaults[param_name] = ServiceParam(**param)

    # self.service_config is the config from the file itself
    try:
      self.service_config = read_config_file(self.config['config'])
      self.enabled = self.service_config.get('enabled', self.enabled)
    except FileNotFoundError:
      self.service_config = {}
    except json.JSONDecodeError:
      logging.error('error parsing json file. Using defaults only')
      self.service_config = {}


  def install_service(self, firefly, **kwargs):
    logging.info('Installing Service %s' % self.name)
    if not self.enabled:
      logging.info('Service %s is not enabled' % self.name)
      return False
    #try:
    config_object = self.get_config()
    logging.info('Service Config: %s' % str(config_object.__dict__))
    firefly.install_package(self.package, alias=self.name, ff_id=self.ff_id, service_package=self, config=config_object)
    self.installed = True
    return True
    #except ValueError:
    #  logging.error('missing required values for service: %s' % self.name)
    #except Exception as e:
    #  logging.error('unknown error installing service: %s (%s)' % (self.name, e))
    return False

  def get_config_value(self, config_index, accept_default=True, fix_with_default=True, missing_okay=False):
    """ Gets the config value from the config file.
    If the value is not in the file and a default is okay, return the default value.


    Raises ValueError if required value not set. If config_index not found raises KeyError
    Args:
      config_index: config file in list of config.
      accept_default: okay to take default values
      missing_okay: okay if required values missing

    Returns:

    """
    if config_index in self.defaults:
      param = self.defaults[config_index]
      if config_index in self.service_config:
        config_value = self.service_config[config_index]
        if config_value is None and not (param.self_init or param.default_init):
          if fix_with_default:
            return param.default
          return raise_value_error(config_value, missing_okay)
        return config_value
      if accept_default:
        config_value = param.default
        if config_value is None and not (param.self_init or param.default_init):
          return raise_value_error(config_value, missing_okay)
        return config_value

    elif config_index in self.required:
      param = self.required[config_index]
      if config_index in self.service_config:
        config_value = self.service_config[config_index]
        if config_value is None and not (param.self_init or param.default_init):
          if fix_with_default:
            return raise_value_error(param.default, missing_okay)
          return raise_value_error(config_value, missing_okay)
        return config_value
      if accept_default:
        config_value = param.default
        if config_value is None and not (param.self_init or param.default_init):
          return raise_value_error(config_value, missing_okay)
        return config_value
      return raise_value_error(None, missing_okay)

    raise KeyError

  def get_config(self, missing_okay=False):
    """ Generates a config object from all the values. Raises errors if values are missing.

    Args:
      missing_okay: okay to not fail on missing values.

    Returns: ServiceConfig Object

    """
    config_items = set(self.defaults)
    config_items.update(self.required)
    config_object = ServiceConfig(self.config['config'], self.enabled)
    for item in config_items:
      config_object.set_item(item, self.get_config_value(item, missing_okay=missing_okay))
    return config_object

  def refresh_file(self):
    try:
      self.service_config = read_config_file(self.config['config'])
    except FileNotFoundError:
      self.service_config = {}

  def save_config(self, config_object: ServiceConfig):
    try:
      with open(self.config['config'], 'w+') as config_file:
        json.dump(config_object.json(), config_file, indent=4, sort_keys=True)
        return True
    except Exception as e:
      logging.error('error writing config to file: %s' % e)
      return False


class ServiceHandler(object):
  def __init__(self, service_packages=SERVICE_PACKAGE_FILE):
    logging.info(service_packages)
    self.service_packages_file = service_packages
    with open(service_packages, 'rb') as sp:
      self.service_packages = json.load(sp)

    # self.services: Dict[str, ServicePackage] = {}
    self.services = {}
    for service in self.service_packages:
      logging.info('New Service Package %s' % str(service))
      new_service = ServicePackage(**service)
      self.services[new_service.ff_id] = new_service

  def get_service_by_name(self, service_name):
    for ff_id, service in self.services.items():
      if service.name.lower() == service_name.lower():
        return service
    return None

  def get_service(self, ff_id):
    if ff_id in self.services:
      return self.services.get(ff_id)
    return None

  def generate_config(self, ff_id, **kwargs):
    config_object = self.services[ff_id].get_config(missing_okay=True)
    for item, value in kwargs.items():
      config_object.set_item(item, value)
    config_object.save()
    self.services[ff_id].refresh_file()
    try:
      config_object = self.services[ff_id].get_config()
      config_object.reload()
      return config_object
    except:
      return False

  def install_service(self, firefly, service_name, config_args={}):
    for ff_id, service in self.services.items():
      if service.name != service_name and ff_id != service_name:
        continue
      new_config = self.generate_config(ff_id, **config_args)
      service.refresh_file()
      if new_config.enabled:
        service.install_service(firefly)
        return True
    return False

  def install_services(self, firefly):
    """ Tries to install all services that are enabled.

    Args:
      firefly: Firefly Object
    """
    logging.info('services: %s ' % str(self.services))
    for ff_id, service in self.services.items():
      logging.info('Looking at installing service %s' % ff_id)
      if service.enabled:
        logging.info('Service %s is enabled.' % ff_id)
        try:
          service.install_service(firefly)
        except:
          logging.info('Error installing service')
      else:
        logging.info('Service %s is not enabled.' % ff_id)

  def get_installed_services(self, firefly):
    """ Gets list of installed services.

    Returns: List of installed services

    """
    installed_services = []
    for ff_id, service in self.services.items():
      if service.installed and ff_id in firefly.components:
        installed_services.append(ff_id)
    return installed_services



