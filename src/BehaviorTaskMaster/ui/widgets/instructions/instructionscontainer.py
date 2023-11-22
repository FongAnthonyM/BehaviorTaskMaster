""" instructionscontainer.py
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
import pathlib

# Third-Party Packages #

# Local Packages #
from ..base import BaseWidgetContainer
from .instructionswidget import InstructionsWidget


# Definitions #
# Classes #
class InstructionsContainer(BaseWidgetContainer):
    def __init__(self, name="Instructions", path=None, events=None, init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack

        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('instructions.txt')
        else:
            self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def construct_widget(self):
        self.widget = InstructionsWidget()

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        self.load_text()
        event = {'SubType': 'InstructionsStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def load_text(self):
        with self.path.open('r') as file:
            self.widget.text = file.read()
        self.widget.set_text()
