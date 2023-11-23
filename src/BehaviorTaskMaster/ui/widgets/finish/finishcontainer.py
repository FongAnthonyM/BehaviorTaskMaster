""" finishcontainer.py
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
from .finishwidget import FinishWidget


# Definitions #
# Classes #
class FinishContainer(BaseWidgetContainer):
    def __init__(self, name="Finish", path=None, events=None, init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self._run_action = self.finish_process

        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('default_image.jpg')
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

    @property
    def run_action(self):
        try:
            out = self.widget.run_action
        except AttributeError:
            out = self._run_action
        return out

    @run_action.setter
    def run_action(self, value):
        self._run_action = value
        if self.widget is not None:
            self.widget.run_action = value

    def construct_widget(self):
        self.widget = FinishWidget()
        self.widget.run_action = self._run_action

    def run(self, path=None):
        if path is not None:
            self.path = path
        self.widget.load_file(self.path)
        event = {}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="TaskFinished", **event)
        self.widget.start()

    def finish_process(self, event=None, caller=None):
        self.events.append(**event)
        self.events.close()
