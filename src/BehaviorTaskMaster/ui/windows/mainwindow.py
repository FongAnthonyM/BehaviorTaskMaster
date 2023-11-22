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
from PySide2.QtWidgets import QMainWindow, QHBoxLayout, QStackedWidget

# Local Packages #
from ..widgets import WidgetStack


# Definitions #
# Classes #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_stack = WidgetStack(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget_stack)
        self.setLayout(self.layout)

        self.setCentralWidget(self.widget_stack)
