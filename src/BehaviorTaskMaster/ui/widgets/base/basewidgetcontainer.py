""" basewidgetcontainer.py
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
class BaseWidgetContainer(ABC):
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
