#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" emotiondialtask.py
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
from ....ui import BaseWidgetContainer
from .categorizationparameterswidget import CategorizationParametersWidget

# Definitions #
# Constants #
START_DIR = ""


# Classes #
class CategorizationParametersContainer(BaseWidgetContainer):
    def __init__(self, name="EmotionParameters", init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack

        self._parameters = None

    @property
    def parameters(self):
        try:
            out = self.widget.parameters
            self._parameters = out
        except:
            out = self._parameters
        return out

    @property
    def loops(self):
        return self.widget.loops

    @property
    def randomize(self):
        return self.widget.randomize

    def construct_widget(self):
        self.widget = CategorizationParametersWidget()

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        super().run()
