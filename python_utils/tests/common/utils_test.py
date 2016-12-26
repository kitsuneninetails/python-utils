import unittest
from python_utils.common import string_utils
from python_utils.tests.utils.test_utils import run_unit_test


class UtilsTest(unittest.TestCase):
    def test_check_string_for_tag(self):
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "foo"))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "fo"))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "bar"))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "foo bar"))
        self.assertTrue(
            string_utils.check_string_for_tag("foo foo baz", "foo", 2))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar foo", "foo", 2))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar bar", "bar", 2))
        self.assertTrue(
            string_utils.check_string_for_tag("foo foo baz", "foo", 1,
                                              exact=False))
        self.assertTrue(
            string_utils.check_string_for_tag("foo foo foo", "foo", 2,
                                              exact=False))
        self.assertTrue(
            string_utils.check_string_for_tag("foo foo baz", "foo", 2,
                                              exact=False))
        self.assertTrue(
            string_utils.check_string_for_tag("foo foo foo", "foo", 3,
                                              exact=False))

        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "bamf"))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "foot"))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "foo", 2))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "baz", 3))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar bar", "foo bar", 2))
        self.assertFalse(
            string_utils.check_string_for_tag("foo barfoo barfoo",
                                              "foo barfoo", 2))
        self.assertFalse(
            string_utils.check_string_for_tag("foo foo baz", "foo", 1))
        self.assertFalse(
            string_utils.check_string_for_tag("foo foo baz", "foo", 3,
                                              exact=False))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "bar", 2,
                                              exact=False))
        self.assertFalse(
            string_utils.check_string_for_tag("foo barfoo barfoo",
                                              "foo barfoo", 2,
                                              exact=False))

        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "bamf", 0))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "bamf", 0,
                                              exact=False))
        self.assertTrue(
            string_utils.check_string_for_tag("foo bar baz", "foo", 0,
                                              exact=False))

        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "foo", 0))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "bar", 0))
        self.assertFalse(
            string_utils.check_string_for_tag("foo bar baz", "baz", 0))

run_unit_test(UtilsTest)
