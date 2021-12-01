#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" utilitywidgets.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2019, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #
from abc import ABC, abstractmethod

# Downloaded Libraries #
from bidict import bidict
from PySide2.QtWidgets import QMainWindow, QHBoxLayout, QStackedWidget

# Local Libraries #


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


class WidgetContainer(ABC):
    def __init__(self, name="", init=False):
        self.name = name

        self.widget = None
        self.widget_stack = None
        self.return_widget = None

        if init:
            self.construct_widget()

    @abstractmethod
    def construct_widget(self):
        self.widget = None

    def destroy_widget(self):
        self.widget = None

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.construct_widget()
        if stack is not None:
            self.widget_stack = stack
        if name is None:
            name = self.name

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.widget_stack.add(self.widget, name)

    def remove_from_stack(self, stack=None, back=True, clear_widget=False, **kwargs):
        if stack is not None:
            self.widget_stack = stack
        if back:
            self.widget_stack.set(self.return_widget)

        self.widget_stack.remove(self.name)

        if clear_widget:
            self.widget = None

    def make_active(self):
        self.widget_stack.set(self.name)

    def run(self):
        self.widget_stack.set(self.name)


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
            self.sequence.append({"widget": widget, "kwargs": kwargs})
            return len(self.sequence)
        else:
            self.sequence.insert(index, {"widget": widget, "kwargs": kwargs})
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
        return info["widget"], info["kwargs"], self.index

    def next(self):
        info = self.sequence[self.next_index()]
        return info["widget"], info["kwargs"], self.next_index()

    def increment_index(self):
        self.index = self.next_index()

    def run_current(self):
        widget = self.sequence[self.index]["widget"]
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


class MainStackedWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_stack = WidgetStack(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget_stack)
        self.setLayout(self.layout)

        self.setCentralWidget(self.widget_stack)
