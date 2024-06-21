# -*- coding: utf-8 -*-
#
# Licensed under the terms of the BSD 3-Clause
# (see plotpy/LICENSE for details)

"""
plotpy benchmarks
=================
"""

from .test_benchmarks import test_benchmarks


def run() -> None:
    """Run plotpy benchmarks"""
    test_benchmarks()


if __name__ == "__main__":
    run()
