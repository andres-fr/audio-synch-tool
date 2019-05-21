# -*- coding:utf-8 -*-


"""
Dummy test to exemplify nested test structures. All directories must include
an empty __init__.py file
"""


import unittest
from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar


class QuackTestCaseCpu(unittest.TestCase):
    """
    """
    def test_dummy(self):
        """
        """
        f = Foo()
        b = Bar()
        f.loop(100)
        b.loop(3)
        fb = f.get_result()+b.get_result()
        self.assertEqual(fb, 103)
