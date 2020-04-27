##
# Copyright 2020: Niel Swart
# Author: Niel Swart
#
##
from util import signal_filter


def test_calc_volume():
    """
    """


def test_filter():

    samples = [350, 36, 354, 345, 330, 650, 123, 330]

    ave = signal_filter(samples)

    assert ave - 341.67 < 1
