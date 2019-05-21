# -*- coding:utf-8 -*-


"""
Small script that runs some arbitrary code and checks for runtime.
It exits with 1 if max usage at any point surpasses specified, and 0 otherwise.
"""

import sys
import argparse
import cProfile
import pstats
from io import StringIO
#
import environment  # noqa: F401
from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar
from dummyapp import do_loop


def get_total_time_and_calls(fn, sort_by="time"):
    """
    This function calls the given a parameterless functor while benchmarking
    it via cProfile. A report is printed to the terminal and the tuple
    (n_seconds, n_calls) is returned.
    """
    pr = cProfile.Profile()
    pr.enable()
    fn()
    pr.disable()
    #
    s = StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats(sort_by)
    ps.print_stats()
    print(s.getvalue())
    #
    return ps.total_tt, ps.total_calls


if __name__ == "__main__":
    #
    print("\n\n")
    print("==================================================================")
    print("               STARTED RUNTIME BENCHMARKING")
    print("==================================================================")
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_seconds_allowed",
                        type=float, default=5.0,  # 1GB allowed by default
                        help="Positive float representing max allowed runtime \
                        in seconds")
    args = parser.parse_args()
    #
    MAX_ALLOWED = args.max_seconds_allowed
    assert MAX_ALLOWED > 0, "argument -m has to be positive, and was "\
        + str(MAX_ALLOWED)
    #
    MEMSIZE = 1000000
    LOOPSIZE = 100
    #
    foo_secs, _ = get_total_time_and_calls(
        lambda: do_loop(Foo, MEMSIZE, LOOPSIZE))
    bar_secs, _ = get_total_time_and_calls(
        lambda: do_loop(Bar, MEMSIZE, LOOPSIZE))
    #
    print("Foo elapsed seconds:", foo_secs)
    print("Bar elapsed seconds:", bar_secs)
    print("Max allowed seconds:", MAX_ALLOWED)
    print("==================================================================")
    print("\n\n")
    #
    if foo_secs > MAX_ALLOWED or bar_secs > MAX_ALLOWED:
        sys.exit(1)
    else:
        # exit(0) means all went well
        sys.exit(0)
