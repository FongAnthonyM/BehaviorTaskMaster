""" utilitywidgets.py
Description:
"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from abc import ABC, abstractmethod

# Third-Party Packages #

# Local Packages #


# Definitions #
# Classes #
class WidgetContainerSequencer:
    def __init__(self):
        self.index = None
        self.sequence = []
        self.loop = False

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.loop and self.index >= len(self.sequence):
            raise StopIteration
        return self.preincrement()

    def insert(self, widget, index=None, **kwargs):
        if index is None:
            self.sequence.append({"windows": widget, "kwargs": kwargs})
            return len(self.sequence)
        else:
            self.sequence.insert(index, {"windows": widget, "kwargs": kwargs})
            return index

    def remove(self, index):
        del self.sequence[index]

    def pop(self, index=-1):
        return self.sequence.pop(index)

    def clear(self):
        self.sequence.clear()
        self.index = None

    def next_index(self):
        if isinstance(self.index, int) and self.index + 1 < len(self.sequence):
            return self.index + 1
        else:
            return 0

    def current(self):
        info = self.sequence[self.index]
        return info["windows"], info["kwargs"], self.index

    def next(self):
        info = self.sequence[self.next_index()]
        return info["windows"], info["kwargs"], self.next_index()

    def increment_index(self):
        self.index = self.next_index()

    def run_current(self):
        widget = self.sequence[self.index]["windows"]
        kwargs = self.sequence[self.index]["kwargs"]
        return widget.run(**kwargs)

    def start(self):
        self.index = 0
        return self.run_current()

    def reset(self):
        self.index = None

    def preincrement(self):
        self.index = self.next_index()
        return self.run_current()

    def postincrement(self):
        output = self.run_current()
        self.index = self.next_index()
        return output

    def skip(self):
        self.index = self.next_index()
        return self.index
