# -*- coding:utf-8 -*-


"""
Unit testing of the dummypackage.foo_module. Doc:
https://docs.python.org/3/library/unittest.html#assert-methods
"""


import unittest
from dummypackage.foo_module import Foo


class FooTestCaseCpu(unittest.TestCase):
    """
    Basic testing of class Foo with minimal coverage
    """
    CLASS = Foo

    def test_init_parameter(self):
        """
        Constructor expects an error if given anything but a positive int:
        """
        self.assertRaises(TypeError, self.CLASS, 123.456)
        self.assertRaises(TypeError, self.CLASS, None)
        self.assertRaises(AssertionError, self.CLASS, 0)
        self.assertRaises(AssertionError, self.CLASS, -1)

    def test_loop(self):
        """
        Some testing of loop
        """
        v1, v2 = 2, 3
        f = self.CLASS()
        #
        f.loop(v1)
        self.assertEqual(f.get_result(), v1)
        #
        f.loop(v2)
        self.assertEqual(f.get_result(), v2)
