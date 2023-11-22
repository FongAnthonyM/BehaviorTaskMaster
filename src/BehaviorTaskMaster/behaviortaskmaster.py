#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" behaviortaskmaster.py
Description:
"""
# Package Header #
from .header import *

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
from .ui import MainMenuWidget, MainWindow


# Definitions #
# Classes #
class BehaviorTaskWindow(MainWindow):
    def __init__(self):
        super(BehaviorTaskWindow, self).__init__()
        self.tasks = dict()
        self.selected_task = None
        self.default_widget = "MainMenu"

        self.main_menu = MainMenuWidget()
        self.main_menu.double_click_action = self.double_click_action
        self.main_menu.selected_action = self.select_action
        self.widget_stack.add(self.main_menu, "MainMenu")

        self.fullscreenAction = None
        self._constuct_fullscreenAction()

    def add_task(self, task, name, text):
        self.tasks[name] = task
        self.main_menu.add_item(text, name)

    def double_click_action(self, index):
        _, name, _ = self.main_menu.find_item(index.row())
        self.selected_task = self.tasks[name]
        self.selected_task.load_task(self.widget_stack)
        self.selected_task.setup_task()

    def select_action(self):
        self.selected_task = self.tasks[self.main_menu.selected_item]
        self.selected_task.load_task(self.widget_stack)
        self.selected_task.setup_task()

    def _constuct_fullscreenAction(self):
        self.fullscreenAction = QAction("FullScreen", self)
        self.fullscreenAction.setShortcut(QKeySequence.FullScreen)
        self.fullscreenAction.triggered.connect(self.fullscreen_action)
        self.addAction(self.fullscreenAction)

    def fullscreen_action(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
