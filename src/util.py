##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

import math


class StringBuilder:
    def __init__(self):
        self.string = []

    def add(self, text):
        if text is None or text == "":
            return self
        self.string.append(str(text))
        return self

    def space(self):
        self.string.append(" ")
        return self

    def newline(self):
        self.string.append("\r\n")
        return self

    def semicolon(self):
        self.string.append("; ")
        return self

    def build(self):
        return "".join(self.string)


class Logger:
    """
    This is a simple singleton implementation of a logger

    NOTE: It is not a thread safe singleton implementation
    """

    _instance = None

    @classmethod
    def getLogger(cls):
        if cls._instance is not None:
            return cls._instance
        else:
            cls._instance = Logger()
            return cls._instance

    def info(self, message: str):
        print("INFO: " + message)

    def severe(self, message: str):
        print("SEVERE: " + message)

    def warn(self, message: str):
        print("WARN: " + message)


def signal_filter(samples):
    samples.sort()

    if len(samples) > 3:
        medi = math.floor(len(samples) / 2)
        ave = (samples[medi - 1] + samples[medi] + samples[medi + 1]) / 3
    elif len(samples) >= 1:
        ave = samples[math.floor(len(samples) / 2)]
    else:
        ave = 0
    return math.trunc(ave)
