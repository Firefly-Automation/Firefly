import logging
import inspect
import os

LOGGING_LEVEL = {
  'debug':    logging.DEBUG,
  'info':     logging.INFO,
  'warn':     logging.WARNING,
  'error':    logging.ERROR,
  'critical': logging.CRITICAL
}


class FireflyLogging(object):
  '''FireflyLogging waraps the default logging module.

  Using FireflyLogging allows logging messages to also go into the database be be used and displayed in the ui. This is
  a work in progress and only logs out to the screen now.
  '''

  def __init__(self, filename=None, level='debug'):
    if filename:
      logging.basicConfig(filename=filename)
    logging.basicConfig(level=LOGGING_LEVEL[level], format='%(asctime)s\t%(levelname)s:\t%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

  def debug(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.debug('%-130s [%s - %s]' % (message, function_name, file_name))

  def info(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def message(self, message):
    ''' message will also show up in the ui logs by defaults but logs as info'''
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.info('%-130s [%s - %s]' % (message, function_name, file_name))

  def warn(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.warning('%-130s [%s - %s]' % (message, function_name, file_name))

  def error(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.error('%-130s [%s - %s]' % (message, function_name, file_name))

  def critical(self, message):
    func = inspect.currentframe().f_back.f_code
    function_name = func.co_name
    file_name = os.path.basename(func.co_filename)
    logging.critical('%-130s [%s - %s]' % (message, function_name, file_name))