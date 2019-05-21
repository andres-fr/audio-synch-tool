# -*- coding:utf-8 -*-


"""
Module mimicking foo with more expensive memory and runtime requirements.
"""

from .foo_module import Foo


class Bar(Foo):
    """
    Similar to Foo, with higher memory and runtime requirements.
    """

    def __init__(self, size=1000000):
        """
        The instance will contain a list instead of a range, so memory
        complexity is O(n) instead of 2*O(1)
        """
        super(Bar, self).__init__(size)
        self._x = list(self._x)  # memory overhead

    def _computation(self):
        """
        The computation will be 2*O(n) instead of O(1)
        """
        super(Bar, self)._computation()
        self._x.index(len(self._x) - 1)  # runtime overhead
