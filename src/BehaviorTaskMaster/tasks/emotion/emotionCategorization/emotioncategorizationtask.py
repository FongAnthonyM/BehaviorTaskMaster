""" emotioncategorizationtask.py
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
from src.BehaviorTaskMaster.ui.widgets import InstructionsContainer, WashoutContainer, FinishContainer, VideoPlayerContainer, QuestionnaireContainer
from src.BehaviorTaskMaster.ui.widgets import VideoPlayerControlContainer
from src.BehaviorTaskMaster.ui.widgets import VideoConfigurationParametersContainer, VideoPlayerControlWidget


# Definitions #
# Classes #
class EmotionCategorizationTask:
    EXPERIMENT_NAME = "Emotion Categorization"

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
        self.control = VideoPlayerControlContainer(events=self.events, x_name=self.EXPERIMENT_NAME)
        self.instructions = InstructionsContainer(path=pathlib.Path(__file__).parent.joinpath('instructions.txt'), events=self.events)
        self.video_player = VideoPlayerContainer(events=self.events)
        self.questionnaire = QuestionnaireContainer(events=self.events)
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


class ControlWidget(VideoPlayerControlWidget):
    header = ('Video', 'Questions', 'Washout', '')

    def _fill_queue(self):
        for i, block in enumerate(self.blocks):
            self.add_item(self.queue_model, _id=i, video=block['video'], configuration=block['questions'])

    @staticmethod
    def add_item(model, _id=0, index=-1, video=None, configuration=None, washout=0):
        # Make Row Objects
        id_number = QtGui.QStandardItem(str(_id))
        video_name = QtGui.QStandardItem(video.name)
        questions_name = QtGui.QStandardItem(question.name)
        washout_name = QtGui.QStandardItem(str(configuration) + "s")

        # Row Settings
        video_name.setEditable(False)
        video_name.setDragEnabled(True)
        video_name.setDropEnabled(False)
        questions_name.setEditable(False)
        questions_name.setDropEnabled(False)
        washout_name.setEditable(False)
        washout_name.setDropEnabled(False)
        id_number.setEnabled(False)
        id_number.setDropEnabled(False)

        if index == -1:
            index = model.rowCount()
            model.appendRow(video_name)
        else:
            model.insertRow(index, video_name)
        model.setItem(index, 1, questions_name)
        model.setItem(index, 2, washout_name)
        model.setItem(index, 3, id_number)

    def start_sequence(self):
        self.sequencer.clear()
        block_sequence = self.sequence_order.index('*block*')
        sequence_order = self.sequence_order[:block_sequence]

        if len(sequence_order) > 1:
            first = sequence_order.pop(0)
            self.sequencer.insert(self.block_widgets[first], ok_action=self.advance, back_action=self.task_window.hide)
        last = sequence_order.pop()
        for item in sequence_order:
            self.sequencer.insert(self.block_widgets[item], ok_action=self.advance)
        self.sequencer.insert(self.block_widgets[last], ok_action=self.advance_block)

    def end_sequence(self):
        block = self.blocks[-1]
        block_sequence = self.sequence_order.index('*block*')
        sequence_order = self.sequence_order[block_sequence + 1:]

        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000,
                              timer_action=self.advance)
        self.sequencer.insert(self.block_widgets['finish'])

    def next_queue(self):
        if self.playing_model.rowCount() > 0:
            complete_index = int(self.playing_model.item(0, 3).text())
            complete = self.blocks[complete_index]
            self.add_item(self.complete_model, _id=complete_index, video=complete['video'],
                          configuration=complete['questions'])

        self.playing_model.clear()
        self.playing_model.setHorizontalHeaderLabels(self.header)
        if self.queue_model.rowCount() > 0:
            play_index = int(self.queue_model.item(0, 3).text())
            block = self.blocks[play_index]

            self.add_item(self.playing_model, _id=play_index, video=block['video'], configuration=block['questions'])
            self.queue_model.removeRow(0)
            flag = True
        else:
            flag = False

        return flag

    def next_block(self):
        play_index = int(self.playing_model.item(0, 3).text())
        block = self.blocks[play_index]

        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000,
                              timer_action=self.advance)
        # self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance_trigger)
        self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance)
        self.sequencer.insert(self.block_widgets['questionnaire'], path=block['questions'],
                              finish_action=self.advance_block)

