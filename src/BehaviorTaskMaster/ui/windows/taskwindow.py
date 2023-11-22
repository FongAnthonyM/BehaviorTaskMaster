""" taskwindow.py
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
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction

# Local Packages #
from ..widgets import WidgetStack


# Definitions #
# Classes #
class TaskWindow(WidgetStack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sequencer = None

        self.fullscreenAction = QAction("FullScreen", self)
        self.fullscreenAction.setShortcut(QKeySequence.FullScreen)
        self.fullscreenAction.triggered.connect(self.fullscreen_action)
        self.addAction(self.fullscreenAction)

    def fullscreen_action(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
