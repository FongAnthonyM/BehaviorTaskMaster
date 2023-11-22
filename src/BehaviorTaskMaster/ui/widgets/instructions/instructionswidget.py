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
import sys

# Third-Party Packages #
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction

# Local Packages #
from .instructions import Ui_Instructions


# Definitions #
# Classes #
class InstructionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self.ui = Ui_Instructions()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.ok)
        self.ui.backButton.clicked.connect(self.back)

        self.okAction = QAction("OK", self)
        self.okAction.setShortcut(QKeySequence("Shift+Return"))
        self.okAction.triggered.connect(self.ok_action)
        self.addAction(self.okAction)

        self.text = None

    def set_text(self, text=None):
        if text is not None:
            self.text = text
        self.ui.textBrowser.setText(self.text)

    def ok(self):
        event = {'type_': 'Instructions', 'Accepted': True}
        self.ok_action(event=event, caller=self)

    def default_ok(self, event=None, caller=None):
        print("Not Connected")

    def back(self):
        event = {'type_': 'Instructions', 'Accepted': False}
        self.back_action(event=event, caller=self)

    def default_back(self, event=None, caller=None):
        sys.exit()
