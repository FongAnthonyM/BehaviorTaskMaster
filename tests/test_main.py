#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_main.py
Description:
"""
# Package Header #
from src.BehaviorTaskMaster.header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import sys

# Third-Party Packages #
from PySide2.QtWidgets import QApplication

# Local Packages #
from src.BehaviorTaskMaster.tasks.emotion import EmotionCategorizationTask
from src.BehaviorTaskMaster.tasks.emotion import RatingTask
from src.BehaviorTaskMaster.tasks.emotion import EmotionCategorizationDialTask
from src.BehaviorTaskMaster.tasks.emotion import RatingDialTask
from src.BehaviorTaskMaster.tasks.emotion import EmotionDialTask
from src.BehaviorTaskMaster.tasks.emotion import EmotionDialQuestionsTask
from src.BehaviorTaskMaster.tasks.emotion import EmotionStimTask
from src.BehaviorTaskMaster import BehaviorTaskWindow


# Definitions #
# Classes #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(RatingTask(window), "RatingTask", "Emotion Rating")
    window.add_task(RatingDialTask(window), "RatingDialTask", "Emotion Rating with Dial")
    window.add_task(EmotionStimTask(window), "EmotionStim", "Emotion Stimulation Control")
    window.add_task(EmotionCategorizationTask(window), "EmotionCategorizationTask", "Emotion Categorization")
    window.add_task(EmotionCategorizationDialTask(window), "EmotionCategorizationDialTask", "Emotion Categorization with Dial")
    window.add_task(EmotionDialTask(window), "EmotionDialTask", "Emotion Dial")
    window.add_task(EmotionDialQuestionsTask(window), "EmotionDialQuestions", "Emotion Dial Alternative")

    window.show()

    sys.exit(app.exec_())

