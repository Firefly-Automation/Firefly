import unittest
from unittest.mock import patch, PropertyMock, Mock
from Firefly import Scheduler
from Firefly.helpers.location import Location
from Firefly.helpers.events import Event
from Firefly.const import EVENT_TYPE_BROADCAST, SOURCE_LOCATION

# Change this to false if you are not connected to the internet.
SETUP_LOCATION = True


class TestFirefly(unittest.TestCase):
  def __init__(self):
    super().__init__()
    self._firefly = None

  @patch('Firefly.core.Firefly')
  def setUp(self, firefly):
    self._firefly = firefly
    self._firefly.scheduler = Scheduler()
    self._firefly.location = Location(self._firefly, '96110', ['home', 'away'], setup=SETUP_LOCATION)

    self._firefly.send_event = Mock(return_value=True)


class MyTest(unittest.TestCase):
  @patch('Firefly.core.Firefly')
  def setUp(self, firefly):
    test_firefly = TestFirefly()
    test_firefly.setUp()
    self._firefly = test_firefly._firefly

  def test_mode(self):
    mode = self._firefly.location.mode
    self.assertEqual(mode, 'home')
    self.assertEqual(self._firefly.location.lastMode, 'home')

  # TODO(zpriddy): Re-enable this test when importing and exporting location works.
  #@unittest.skip("classing skipping")
  @unittest.skipIf(SETUP_LOCATION is False, "Location currently has to be setup to test this.")
  def test_change_mode(self):
    self._firefly.location.mode = 'away'
    self.assertEqual('away', self._firefly.location.mode)
    self.assertEqual('home', self._firefly.location.lastMode)
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, {
        'EVENT_ACTION_MODE': 'away',
        'mode':              'away',
        'last_mode':         'home',
        'is_dark':           self._firefly.location.isDark
    })
    Mock.assert_called_with(self._firefly.send_event, event)

    self._firefly.location.mode = 'home'
    self.assertEqual('home', self._firefly.location.mode)
    self.assertEqual('away', self._firefly.location.lastMode)
    event = Event(SOURCE_LOCATION, EVENT_TYPE_BROADCAST, {
        'EVENT_ACTION_MODE': 'home',
        'mode':              'home',
        'last_mode':         'away',
        'is_dark':           self._firefly.location.isDark
    })
    Mock.assert_called_with(self._firefly.send_event, event)
