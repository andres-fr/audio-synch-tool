# -*- coding:utf-8 -*-


"""
Dummy app using the functionality in dummypackage.
"""

from time import time
#
from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar
from dummypackage.nested.baz_module import Baz


def do_loop(clss, memsize, loopsize):
    """
    Create a Foo instance and loop it.
    """
    print("called do_loop:", (clss.__name__, memsize, loopsize))
    x = clss(memsize)
    t = time()
    x.loop(loopsize)
    print("  do_loop took", time()-t, "seconds")


if __name__ == "__main__":
    MEMSIZE = 1000000
    LOOPSIZE = 100
    do_loop(Foo, MEMSIZE, LOOPSIZE)
    do_loop(Bar, MEMSIZE, LOOPSIZE)
    print("Baz says", Baz.d)
