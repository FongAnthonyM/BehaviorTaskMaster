""" washoutwidget.py
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

# Local Packages #
from ..base import BaseWidgetContainer
from .washoutwidget import WashoutWidget


# Definitions #
# Classes #
class WashoutContainer(BaseWidgetContainer):
    def __init__(self, name="Washout", events=None, init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self.timer_action = None

        self.events = events

        self.milliseconds = 0
        self.font_size = 100
        self.text = "X"

    def construct_widget(self):
        self.widget = WashoutWidget()

    def run(self, milliseconds=None, timer_action=None):
        if milliseconds is not None:
            self.milliseconds = milliseconds
        if timer_action is not None:
            self.timer_action = timer_action

        self.widget.timer_action = self.timer_action
        self.widget.milliseconds = self.milliseconds
        event = {'SubType': 'WashoutStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)
        self.widget.start()

    def setup(self):
        self.widget.milliseconds = self.milliseconds
        self.widget.set_text(self.text)
        self.widget.set_font_size(self.font_size)
