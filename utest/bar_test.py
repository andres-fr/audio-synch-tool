# -*- coding:utf-8 -*-


"""
Unit testing of the dummypackage.bar_module. Doc:
https://docs.python.org/3/library/unittest.html#assert-methods
"""


from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar
from .foo_test import FooTestCaseCpu


class BarTestCaseCpu(FooTestCaseCpu):
    """
    Applies all the Foo tests to Bar, plus an extra inheritance
    test.
    """
    CLASS = Bar

    def test_inheritance(self):
        """
        Dummy check that Bar inherits from Foo
        """
        b = Bar()
        self.assertIsInstance(b, Bar)
        self.assertIsInstance(b, Foo)
