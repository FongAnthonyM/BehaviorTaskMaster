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
import pathlib

# Third-Party Packages #
from PySide2.QtWidgets import QApplication

# Local Packages #
from src.BehaviorTaskMaster.ui.widgets import RatingWidget


# Definitions #
# Classes #
if __name__ == "__main__":
    r_path = pathlib.Path.cwd().joinpath("rating.toml")
    app = QApplication(sys.argv)

    window = RatingWidget()
    window.load_file(r_path)
    window.show()

    sys.exit(app.exec_())

