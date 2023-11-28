""" ratingtask.py
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
import sys
import pathlib
import copy
import datetime

# Third-Party Packages #
from PySide2 import QtGui, QtWidgets, QtMultimedia
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Packages #
from src.BehaviorTaskMaster.utility.iotriggers import AudioTrigger
from src.BehaviorTaskMaster.utility.eventlogger import SubjectEventLogger
from src.BehaviorTaskMaster.ui.windows import TaskWindow
from src.BehaviorTaskMaster.ui.widgets import BaseWidgetContainer, WidgetContainerSequencer
from src.BehaviorTaskMaster.ui.widgets import InstructionsContainer, WashoutContainer, FinishContainer, VideoPlayerContainer, RatingContainer
from src.BehaviorTaskMaster.ui.widgets import VideoPlayerControlContainer
from src.BehaviorTaskMaster.ui.widgets import VideoConfigurationParametersContainer


# Definitions #
# Classes #
class RatingTask:
    EXPERIMENT_NAME = "Emotion Rating"

    def __init__(self, parent=None, stack=None, r_widget=None):
        self.parent = parent
        self.widget_stack = stack
        self.return_widget = r_widget

        self.trigger = AudioTrigger()
        self.trigger.audio_device.device = 3
        self.trigger.add_square_wave('square_wave', amplitude=5, samples=22000, channels=1)
        self.trigger.current_waveform = 'square_wave'

        self.task_window = TaskWindow()
        self.events = SubjectEventLogger(io_trigger=self.trigger)
        
        self.sequencer = WidgetContainerSequencer()
        self.task_window.sequencer = self.sequencer

        self.parameters = VideoConfigurationParametersContainer()
        self.control = VideoPlayerControlContainer(events=self.events, x_name=self.EXPERIMENT_NAME, path=pathlib.Path(__file__).parent)
        self.instructions = InstructionsContainer(path=pathlib.Path(__file__).parent.joinpath('instructions.txt'), events=self.events)
        self.video_player = VideoPlayerContainer(events=self.events)
        self.questionnaire = RatingContainer(events=self.events)
        self.washout = WashoutContainer(events=self.events)
        self.finished = FinishContainer(events=self.events)

        self.block_widgets = {'instructions': self.instructions, 'video_player': self.video_player,
                              'questionnaire': self.questionnaire, 'washout': self.washout, 'finish': self.finished}
        self.sequence_order = ['instructions', '*block*', 'washout', 'finish']
        self.block_order = ['washout', 'video_player', 'questionnaire']

    def load_task(self, stack=None):
        if stack is not None:
            self.widget_stack = stack

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.widget_stack.load(self.parameters)
        self.widget_stack.load(self.control)

        self.task_window.load(self.instructions)
        self.task_window.load(self.washout)
        self.task_window.load(self.video_player)
        self.task_window.load(self.questionnaire)
        self.task_window.load(self.finished)

        self.control.task_window = self.task_window
        self.control.sequencer = self.sequencer
        self.control.sequence_order = self.sequence_order
        self.control.parameters = self.parameters.parameters
        self.control.block_widgets = self.block_widgets
        self.control.player = self.video_player

    def unload_task(self, back=True, clear_widget=False):
        if back:
            self.widget_stack.set(self.return_widget)

        self.widget_stack.unload(self.parameters, back=False, clear_widget=clear_widget)
        self.widget_stack.unload(self.control, back=False, clear_widget=clear_widget)

        self.task_window.close()
        self.task_window.unload(self.instructions, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.washout, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.video_player, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.questionnaire, back=False, clear_widget=clear_widget)

    def setup_task(self):
        self.parameters.run(self.control_task, self.unload_task)

    def control_task(self):
        self.control.run(self.parameters.run)
