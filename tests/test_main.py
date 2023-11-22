#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_main.py
Description:
"""
# Package Header #
from ...header import *

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
from src.BehaviorTaskMaster.emotion.emotionCategorization.emotioncategorizationtask import EmotionCategorizationTask
from src.BehaviorTaskMaster.emotion.rating.ratingtask import RatingTask
from src.BehaviorTaskMaster.emotion.emotionCategorizationDial.emotioncategorizationdialtask import EmotionCategorizationDialTask
from src.BehaviorTaskMaster.emotion.ratingDial.ratingdialtask import RatingDialTask
from src.BehaviorTaskMaster.emotion.emotionDial.emotiondialtask import EmotionDialTask
from src.BehaviorTaskMaster.emotion.emotionDialQuestions.emotiondialquestionstask import EmotionDialQuestionsTask
from src.BehaviorTaskMaster.emotion.emotionStim.emotionstimtask import EmotionStimTask
from src.BehaviorTaskMaster import BehaviorTaskWindow


# Definitions #
# Classes #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(EmotionCategorizationTask(window), "EmotionCategorizationTask", "Emotion Categorization")
    window.add_task(RatingTask(window), "RatingTask", "Emotion Rating")
    window.add_task(EmotionCategorizationDialTask(window), "EmotionCategorizationDialTask", "Emotion Categorization with Dial")
    window.add_task(RatingDialTask(window), "RatingDialTask", "Emotion Rating with Dial")
    window.add_task(EmotionDialTask(window), "EmotionDialTask", "Emotion Dial")
    window.add_task(EmotionDialQuestionsTask(window), "EmotionDialQuestions", "Emotion Dial Alternative")
    window.add_task(EmotionStimTask(window), "EmotionStim", "Emotion Stimulation Control")

    window.show()

    sys.exit(app.exec_())

