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

# Third-Party Packages #
from bidict import bidict
from PySide2.QtWidgets import QMainWindow, QHBoxLayout, QStackedWidget

# Local Packages #


# Definitions #
# Classes #
class WidgetStack(QStackedWidget):
    def __init__(self, parent=None):
        super(WidgetStack, self).__init__(parent)
        self.keys = bidict()

    def __len__(self):
        return self.count()

    def __getitem__(self, item):
        w, _, _ = self.find_stacked(item)
        return w

    def add(self, w, name, i=-1):
        index = self.insertWidget(i, w)
        self.keys[name] = w
        return index

    def remove(self, w):
        w, name, _ = self.find_stacked(w)
        self.removeWidget(w)
        del self.keys[name]

    def load(self, w_container, name=None, **kwargs):
        if name is None:
            name = w_container.name

        w_container.add_to_stack(stack=self, name=name, **kwargs)

    def unload(self, w_container, **kwargs):
        w_container.remove_from_stack(stack=self, **kwargs)

    def find_stacked(self, w):
        if isinstance(w, str):
            w = self.keys[w]
        elif isinstance(w, int):
            w = self.widget(w)
        name = self.keys.inverse[w]
        index = self.indexOf(w)
        return w, name, index

    def current(self):
        index = self.currentIndex()
        if index == -1:
            return None, None, -1
        else:
            return self.find_stacked(index)

    def set(self, w):
        _, _, i = self.find_stacked(w)
        self.setCurrentIndex(i)
