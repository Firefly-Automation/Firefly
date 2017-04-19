import unittest
from unittest import mock
from unittest.mock import patch, PropertyMock

from Firefly.const import (ACTION_TOGGLE)

from Firefly.helpers.action import Action
from Firefly.helpers.conditions import Conditions


class TestCheckConditions(unittest.TestCase):
  @patch('Firefly.core.Firefly', new_callable=PropertyMock)
  def setUp(self, firefly):
    self.firefly = firefly

  def test_make_action(self):
    c = Conditions(is_dark=True)
    action = Action('test_device', ACTION_TOGGLE, 'test_source', c)
    export_data = action.export()
    self.assertDictEqual(export_data, {
      'ff_id':      'test_device',
      'command':    ACTION_TOGGLE,
      'force':      False,
      'conditions': {
        'is_dark': True
      },
      'source':     'test_source'
    })

  def test_make_action_kwargs(self):
    c = Conditions(is_dark=True)
    action = Action('test_device', ACTION_TOGGLE, 'test_source', c, test='this is a test value')
    export_data = action.export()
    self.assertDictEqual(export_data, {
      'ff_id':      'test_device',
      'command':    ACTION_TOGGLE,
      'force':      False,
      'conditions': {
        'is_dark': True
      },
      'test':       'this is a test value',
      'source':     'test_source'
    })

  def test_import_action(self):
    import_data = {
      'ff_id':      'test_device',
      'command':    ACTION_TOGGLE,
      'force':      False,
      'conditions': {
        'is_dark': True
      },
      'test':       'this is a test value',
      'source':     'test_source'
    }
    action = Action(**import_data)
    export_data = action.export()
    self.assertDictEqual(export_data, {
      'ff_id':      'test_device',
      'command':    ACTION_TOGGLE,
      'force':      False,
      'conditions': {
        'is_dark': True
      },
      'test':       'this is a test value',
      'source':     'test_source'
    })
