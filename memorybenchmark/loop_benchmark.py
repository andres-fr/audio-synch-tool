# -*- coding:utf-8 -*-


"""
Memory benchmarking of the dummypackage functionality
"""

import environment  # noqa: F401
from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar
from memory_profiler import profile


@profile  # decorator for (https://pypi.org/project/memory-profiler/)
def do_loop(clss, memsize, loopsize):
    """
    Create a Foo instance and loop it.
    """
    x = clss(memsize)
    x.loop(loopsize)


if __name__ == "__main__":
    MEMSIZE = 1000000
    LOOPSIZE = 100
    do_loop(Foo, MEMSIZE, LOOPSIZE)
    do_loop(Bar, MEMSIZE, LOOPSIZE)
