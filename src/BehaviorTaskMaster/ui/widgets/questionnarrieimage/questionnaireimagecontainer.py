""" questionnaireimagecontainer.py
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

# Local Packages #
from ..questionnarie import QuestionnaireContainer
from .questionnaireimagewidget import QuestionnaireImageWidget


# Definitions #
# Classes #
class QuestionnaireImageContainer(QuestionnaireContainer):
    def construct_widget(self):
        self.widget = QuestionnaireImageWidget(self._next_action, self._finish_action, self._previous_action, self._back_action, self._answer_action)
