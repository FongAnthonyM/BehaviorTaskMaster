""" videoplayercontainer.py
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
from .videoplayercontrolwidget import VideoPlayerControlWidget


# Definitions #
# Classes #
class VideoPlayerControlContainer(BaseWidgetContainer):
    def __init__(self, name="EmotionControl", x_name="", events=None, init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self.back_action = self.remove_from_stack
        self.experiment_name = x_name
        self._events = events

    @property
    def task_window(self):
        return self.widget.task_window

    @task_window.setter
    def task_window(self, value):
        self.widget.task_window = value

    @property
    def sequencer(self):
        return self.widget.sequencer

    @sequencer.setter
    def sequencer(self, value):
        self.widget.sequencer = value

    @property
    def block_widgets(self):
        return self.widget.block_widgets

    @block_widgets.setter
    def block_widgets(self, value):
        self.widget.block_widgets = value

    @property
    def sequence_order(self):
        return self.widget.sequence_order

    @sequence_order.setter
    def sequence_order(self, value):
        self.widget.sequence_order = value

    @property
    def player(self):
        return self.widget.player

    @player.setter
    def player(self, value):
        self.widget.player = value

    @property
    def parameters(self):
        return self.widget.paremeters

    @parameters.setter
    def parameters(self, value):
        self.widget.parameters = value

    @property
    def events(self):
        try:
            out = self.widget.events
        except AttributeError:
            out = self._events
        return out

    @events.setter
    def events(self, value):
        self._events = value
        if self.widget is not None:
            self.widget.events = value

    def construct_widget(self):
        self.widget = VideoPlayerControlWidget()
        self.widget.events = self._events
        self.widget.experiment_name = self.experiment_name

    def run(self, back_action=None):
        if back_action is not None:
            self.back_action = back_action

        self.widget.back_action = self.back_action
        self.widget.construct()
        self.widget.construct_blocks()
        super().run()
