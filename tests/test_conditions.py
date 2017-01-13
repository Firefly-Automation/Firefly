import unittest
from unittest import mock
from unittest.mock import patch, PropertyMock

from Firefly.const import (IS_DARK, IS_LIGHT, IS_MODE, IS_NOT_MODE, IS_NOT_TIME_RANGE, IS_TIME_RANGE)

from Firefly.util.conditions import check_conditions


class TestCheckConditions(unittest.TestCase):
  @patch('Firefly.core.Firefly', new_callable=PropertyMock)
  def setUp(self, firefly):
    self.firefly = firefly

  def test_is_dark_is_light(self):
    type(self.firefly.location).isDark = PropertyMock(return_value=True)
    type(self.firefly.location).isLight = PropertyMock(return_value=False)
    # Verify Mock
    self.assertTrue(self.firefly.location.isDark)
    self.assertFalse(self.firefly.location.isLight)

    # Do Tests
    condition = {IS_DARK: True}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_DARK: False}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_LIGHT: True}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    type(self.firefly.location).isDark = PropertyMock(return_value=False)
    type(self.firefly.location).isLight = PropertyMock(return_value=True)
    # Verify Mock
    self.assertFalse(self.firefly.location.isDark)
    self.assertTrue(self.firefly.location.isLight)

    # Do Tests
    condition = {IS_DARK: True}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_DARK: False}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_LIGHT: True}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

  def test_check_mode(self):
    type(self.firefly.location).mode = PropertyMock(return_value='Home')
    # Verify Mock
    self.assertEqual(self.firefly.location.mode, 'Home')

    condition = {IS_MODE: ['Home']}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_MODE: 'Home'}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_MODE: ['Home', 'Away']}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_MODE: ['Away']}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_NOT_MODE: ['Away']}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_NOT_MODE: ['Away', 'Home']}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

  def text_multiple_conditions(self):
    type(self.firefly.location).isDark = PropertyMock(return_value=True)
    type(self.firefly.location).isLight = PropertyMock(return_value=False)
    type(self.firefly.location).mode = PropertyMock(return_value='Home')

    condition = {IS_MODE: 'Home', IS_DARK: True, IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_MODE: 'Home', IS_DARK: False, IS_LIGHT: True}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_MODE: 'Home', IS_NOT_MODE: 'Away', IS_DARK: True, IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertTrue(check)

    condition = {IS_MODE: 'Away', IS_NOT_MODE: 'Home', IS_DARK: True, IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_MODE: 'Home', IS_NOT_MODE: 'Home', IS_DARK: True, IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_MODE: 'Home', IS_NOT_MODE: 'Away', IS_DARK: False, IS_LIGHT: False}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_MODE: 'Home', IS_NOT_MODE: 'Away', IS_DARK: False, IS_LIGHT: True}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)

    condition = {IS_MODE: 'Home', IS_NOT_MODE: 'Away', IS_DARK: True, IS_LIGHT: True}
    check = check_conditions(self.firefly, condition)
    self.assertFalse(check)