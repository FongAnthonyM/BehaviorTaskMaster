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
from src.BehaviorTaskMaster.tasks.pain import TemperatureRatingTask
from src.BehaviorTaskMaster import BehaviorTaskWindow


# Definitions #
# Classes #
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(TemperatureRatingTask(window), "TemperatureRatingTask", "Temperature Rating")

    window.show()

    sys.exit(app.exec_())

