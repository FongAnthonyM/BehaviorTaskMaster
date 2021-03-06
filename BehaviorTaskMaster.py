#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" BehaviorTaskMaster.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2019, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #
import sys

# Downloaded Libraries #
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QApplication, QAction

# Local Libraries #
from QtUtility.utilitywidgets import MainStackedWindow
from mainUI.mainUI import MainMenuWidget
from emotionTasks.emotionCategorization.emotioncategorizationtask import EmotionCategorizationTask
from emotionTasks.emotionCategorizationDial.emotioncategorizationdialtask import EmotionCategorizationDialTask
from emotionTasks.emotionDial.emotiondialtask import EmotionDialTask
from emotionTasks.emotionDialQuestions.emotiondialquestionstask import EmotionDialQuestionsTask


# Definitions #
# Classes #
class BehaviorTaskWindow(MainStackedWindow):
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




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(EmotionCategorizationTask(window), "EmotionCategorizationTask", "Emotion Categorization")
    window.add_task(EmotionCategorizationDialTask(window), "EmotionCategorizationDialTask", "Emotion Categorization with Dial")
    window.add_task(EmotionDialTask(window), "EmotionDialTask", "Emotion Dial")
    window.add_task(EmotionDialQuestionsTask(window), "EmotionDialQuestions", "Emotion Dial Alternative")

    window.show()

    sys.exit(app.exec_())
