#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_main.py
Description:
"""
# Package Header #
from src.BehaviorTaskMaster.__header__ import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import sys

# Downloaded Libraries #
from PySide2.QtWidgets import QApplication

# Local Libraries #
from src.BehaviorTaskMaster.emotionTasks.emotionCategorization.emotioncategorizationtask import EmotionCategorizationTask
from src.BehaviorTaskMaster.emotionTasks.emotionCategorizationDial.emotioncategorizationdialtask import EmotionCategorizationDialTask
from src.BehaviorTaskMaster.emotionTasks.emotionDial.emotiondialtask import EmotionDialTask
from src.BehaviorTaskMaster.emotionTasks.emotionDialQuestions.emotiondialquestionstask import EmotionDialQuestionsTask
from src.BehaviorTaskMaster import BehaviorTaskWindow


# Definitions #
# Classes #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(EmotionCategorizationTask(window), "EmotionCategorizationTask", "Emotion Categorization")
    window.add_task(EmotionCategorizationDialTask(window), "EmotionCategorizationDialTask", "Emotion Categorization with Dial")
    window.add_task(EmotionDialTask(window), "EmotionDialTask", "Emotion Dial")
    window.add_task(EmotionDialQuestionsTask(window), "EmotionDialQuestions", "Emotion Dial Alternative")

    window.show()

    sys.exit(app.exec_())

