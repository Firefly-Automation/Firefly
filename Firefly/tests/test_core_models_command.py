#!/usr/bin/python

from core.models.command import Command

import mock 
from mock import patch
import unittest

class send_command:
  def __init__(self, command):
    return False

class CommandTestCase(unittest.TestCase):
  def setUp(self):
    self.deviceID = 'testDevice'
    self.command = {'action':'testAction'}
    self.simpleCommand = "off"
    self.routine = 'testRoutine'

  def test_send_command(self):
    with patch('core.firefly_api.send_command', return_value=True) as mock_send_command:
      s = Command(self.deviceID,self.command)
      self.assertEqual(mock_send_command.call_args[0][0].deviceID, self.deviceID)
      self.assertEqual(mock_send_command.call_args[0][0].command, self.command)
      self.assertFalse(s._simple, 'Simple Command is: {}'.format(s._simple))
      self.assertFalse(s._routine)
      self.assertTrue(s._result)
      mock_send_command.assert_called_once_with(s)

  def test_send_simple_command(self):
    with patch('core.firefly_api.send_command') as mock_send_command:
      s = Command(self.deviceID,self.simpleCommand)
      self.assertEqual(mock_send_command.call_args[0][0].deviceID, self.deviceID)
      self.assertEqual(mock_send_command.call_args[0][0].command, {self.simpleCommand:''})
      self.assertTrue(s._simple)
      self.assertFalse(s._routine)
      mock_send_command.assert_called_once_with(s)

  def test_send_routine_command(self):
    with patch('core.firefly_api.send_command') as mock_send_command:
      s = Command(self.routine, None, routine=True)
      self.assertEqual(mock_send_command.call_args[0][0].deviceID, self.routine)
      self.assertEqual(mock_send_command.call_args[0][0].command, None)
      self.assertFalse(s._simple)
      self.assertTrue(s._routine)
      mock_send_command.assert_called_once_with(s)

  def runTest(self):
    unittest.main(exit=False)

if __name__ == "__main__":
  unittest.main(exit=False)
