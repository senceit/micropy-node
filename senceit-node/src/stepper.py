##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
# Driving a 28BYJ stepper motor with ULN2003 IC
# The motor has 4 coils
# 4 - BLUE
# 3 - PINK
# 2 - YELLOW
# 1 - ORANGE
# COM - RED
##

import time


class Stepper:
    def __init__(self, in1, in2, in3, in4):
        """
        """
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4

        self.in1.off()
        self.in2.off()
        self.in3.off()
        self.in4.off()

    def turn(self, dir, steps, multiple):
        """Turn the stepper `steps` in `dir` direction, `multiple` times

        Parameters
        ----------

        e.g. steps = 1 - 1/2048 revolution
        e.g. deg = 180 - 1/2th turn
        e.g. deg = 360, multiple = 3 - turn 3 times

        Returns
        -------
        """

    def forward(self, steps, multiple=1):
        """
        Turn the stepper deg degrees, multiple times

        e.g. deg = 45 - 1/8th turn
        e.g. deg = 180 - 1/2th turn
        e.g. deg = 360, multiple = 3 - turn 3 times
        """

        for s in range(1, steps):
            self.step()

    def backward(self, deg, multiple=1):
        """
        """

    def step(self):
        # step 1
        self.on(1)
        self.on(2)
        #
        time.sleep_ms(2)
        self.off(1)
        # step 2
        self.on(3)
        #
        time.sleep_ms(2)
        self.off(2)
        # step 3
        self.on(4)
        #
        time.sleep_ms(2)
        self.off(3)
        # step 4
        self.on(1)
        time.sleep_ms(2)
        self.off()

    def off(self, coil=None):
        if coil is None:
            self.in1.off()
            self.in2.off()
            self.in3.off()
            self.in4.off()
        elif coil == 1:
            self.in1.off()
        elif coil == 2:
            self.in2.off()
        elif coil == 3:
            self.in3.off()
        elif coil == 4:
            self.in4.off()

    def on(self, coil):
        if coil is None:
            self.in1.on()
            self.in2.on()
            self.in3.on()
            self.in4.on()
        elif coil == 1:
            self.in1.on()
        elif coil == 2:
            self.in2.on()
        elif coil == 3:
            self.in3.on()
        elif coil == 4:
            self.in4.on()
