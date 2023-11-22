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
import pathlib

# Third-Party Packages #
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtWidgets import QWidget, QAction

# Local Packages #
from .emotionfinish import Ui_EmotionFinish


# Definitions #
# Classes #
class FinishWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._path = None
        self.run_action = self.default_run

        self.ui = Ui_EmotionFinish()
        self.ui.setupUi(self)

        self.text = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def load_file(self, file):
        if file is not None:
            self.path = file
        pixmap = QtGui.QPixmap(self.path.as_posix())
        self.ui.imageSpace.setPixmap(pixmap)

    def start(self):
        event = {'type_': 'Finished'}
        self.run_action(event=event, caller=self)

    def default_run(self, event=None, caller=None):
        print('finish')
