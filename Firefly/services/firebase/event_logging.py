import json
from time import sleep
from os import remove

LOG_PATH = '/opt/firefly_system/logs/event_log_%s.json'
EVENTS_PER_FILE = 2000
REMOVE_FILES = True

class EventLogger(object):
  def __init__(self, firebase, log_file=LOG_PATH):
    self.firebase = firebase
    self.log_file = log_file
    self.event_log = list()
    self.lock = False
    self.lock_count = 0

  def event(self, source, action, ts, **kwargs):
    if source == "time":
      return
    event_line = {
      'timestamp': ts,
      'ff_id': source,
      'event': action
    }

    while self.lock and self.lock_count < 10:
      sleep(1)
      self.lock_count += 1

    if self.lock_count >= 10:
      self.lock_count = 0
      return

    self.lock_count = 0
    self.event_log.append(event_line)

    if len(self.event_log) >= EVENTS_PER_FILE:
      self.write_file(ts)

  def write_file(self, ts):
    # Lock and copy data
    self.lock = True
    data = self.event_log.copy()
    self.event_log = list()
    self.lock = False

    filename = LOG_PATH % str(ts)
    with open(filename, 'w') as fp:
      json.dump(data, fp)

    self.firebase.upload_log(filename)

    if REMOVE_FILES:
      remove(filename)


  def shutdown(self):
    self.write_file()


