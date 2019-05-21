# -*- coding:utf-8 -*-


"""
Small script that runs some arbitrary code and checks for memory usage.
It exits with 1 if max usage at any point surpasses specified, and 0 otherwise.
"""

import sys
import argparse
from memory_profiler import memory_usage
#
import environment  # noqa: F401
from dummypackage.foo_module import Foo
from dummypackage.bar_module import Bar
from dummyapp import do_loop


if __name__ == "__main__":
    #
    print("\n\n")
    print("==================================================================")
    print("               STARTED MEMORY BENCHMARKING")
    print("==================================================================")
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_megabytes_allowed",
                        type=float, default=1024.0,  # 1GB allowed by default
                        help="Positive float representing max allowed memory \
                        usage in MB")
    parser.add_argument("-i", "--time_interval",
                        type=float, default=0.1,  # 0.1 seconds default
                        help="Positive float representing interval between \
                        each memory measurement, in seconds.")

    args = parser.parse_args()
    #
    MAX_ALLOWED = args.max_megabytes_allowed
    assert MAX_ALLOWED > 0, "argument -m has to be positive, and was "\
        + str(MAX_ALLOWED)
    TIME_INTERVAL = args.time_interval
    assert TIME_INTERVAL > 0, "argument -i has to be positive, and was "\
        + str(TIME_INTERVAL)
    #
    MEMSIZE = 1000000
    LOOPSIZE = 100
    foo_mem = memory_usage((do_loop, (Foo, MEMSIZE, LOOPSIZE)),
                           interval=TIME_INTERVAL)
    bar_mem = memory_usage((do_loop, (Bar, MEMSIZE, LOOPSIZE)),
                           interval=TIME_INTERVAL)
    #
    foo_max = max(foo_mem)
    bar_max = max(bar_mem)
    print("Foo max memory consumption (MB):", foo_max)
    print("Bar max memory consumption (MB):", bar_max)
    print("Max allowed memory consumption:", MAX_ALLOWED)
    print("==================================================================")
    print("\n\n")
    #
    if foo_max > MAX_ALLOWED or bar_max > MAX_ALLOWED:
        sys.exit(1)
    else:
        # exit(0) means all went well
        sys.exit(0)
