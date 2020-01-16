#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" emotiondialtask.py
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
import pathlib
import copy
import datetime

# Downloaded Libraries #
from PySide2 import QtGui, QtWidgets, QtMultimedia
from PySide2.QtCore import QDir
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Libraries #
from utility.iotriggers import AudioTrigger
from utility.eventlogger import SubjectEventLogger
from QtUtility.utilitywidgets import WidgetContainer, WidgetContainerSequencer
from QtUtility.taskwidgets import TaskWindow
from emotionTasks.emotionwidgets import EmotionInstructions, EmotionWashout, EmotionFinish, EmotionVideoPlayer, EmotionQuestionnaireImage
from emotionTasks.emotionCategorization.UI.emotionparameters import Ui_EmotionParameters
from emotionTasks.UI.emotioncontrol import Ui_EmotionControl


# Definitions #
# Constants #
START_DIR = ""


# Classes #
class EmotionCategorizationDialTask:
    EXPERIMENT_NAME = "Emotion Categorization with Dial"

    def __init__(self, parent=None, stack=None, r_widget=None):
        self.parent = parent
        self.widget_stack = stack
        self.return_widget = r_widget

        self.trigger = AudioTrigger()
        self.trigger.audio_device.device = 'Headphones 1'
        self.trigger.add_square_wave('square_wave', amplitude=5, samples=22000)
        self.trigger.current_waveform = 'square_wave'

        self.task_window = TaskWindow()
        self.events = SubjectEventLogger(io_trigger=self.trigger)

        self.sequencer = WidgetContainerSequencer()
        self.task_window.sequencer = self.sequencer

        self.parameters = EmotionParameters()
        self.control = EmotionControl(events=self.events, x_name=self.EXPERIMENT_NAME)
        self.instructions = EmotionInstructions(path=pathlib.Path(__file__).parent.joinpath('instructions.txt'),
                                                events=self.events)
        self.video_player = EmotionVideoPlayer(events=self.events)
        self.questionnaire = EmotionQuestionnaireImage(events=self.events)
        self.washout = EmotionWashout(events=self.events)
        self.finished = EmotionFinish(events=self.events)

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


class EmotionParameters(WidgetContainer):
    def __init__(self, name="EmotionParameters", init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack

        self._parameters = None

    @property
    def parameters(self):
        try:
            out = self.widget.parameters
            self._parameters = out
        except:
            out = self._parameters
        return out

    @property
    def loops(self):
        return self.widget.loops

    @property
    def randomize(self):
        return self.widget.randomize

    def construct_widget(self):
        self.widget = ParametersWidget()

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        super().run()


class ParametersWidget(QWidget):
    header = ('Video', 'Questions', 'Video Path', 'Question Path')
    v_types = ('*.avi', '*.mp4', '*.ogg', '*.qt', '*.wmv', '*.yuv')
    q_types = ('*.toml',)

    def __init__(self):
        super(ParametersWidget, self).__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self._parameters = {}
        self.subject = []
        self.session = []
        self.blocks = []

        self.ui = Ui_EmotionParameters()
        self.ui.setupUi(self)

        self.list_model = None
        self._construct_video_list()

        self.deleteAction = None
        self._construct_deleteAction()

        self.okAction = None
        self._construct_okAction()

        self._construct_backAction()

    @property
    def parameters(self):
        self._parameters['subject'] = self.subject
        self._parameters['session'] = self.session
        self._parameters['blocks'] = self.blocks
        return self._parameters

    @property
    def static_parameters(self):
        self._parameters['blocks'] = self.blocks
        self._parameters['loops'] = self.loops
        self._parameters['randomize'] = self.randomize
        return copy.deepcopy(self._parameters)

    def _construct_video_list(self):
        self.list_model = QtGui.QStandardItemModel(0, 4)
        self.list_model.setHorizontalHeaderLabels(self.header)
        self.ui.videoList.setModel(self.list_model)
        self.ui.videoList.setDragDropMode(QAbstractItemView.InternalMove)
        self.ui.videoList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.videoList.setColumnWidth(0, 200)
        self.ui.videoList.setColumnWidth(1, 200)
        self.ui.videoList.setColumnWidth(2, 100)
        self.ui.videoList.setColumnWidth(3, 100)

        self.ui.videoList.doubleClicked.connect(self.double_click)
        self.ui.addVideoButton.clicked.connect(self.add_videos)
        self.ui.addQuestionsButton.clicked.connect(self.add_questions)
        self.ui.videoDirectory.clicked.connect(self.video_directory)
        self.ui.questionDirectory.clicked.connect(self.question_directory)
        self.ui.deleteLastButton.clicked.connect(self.delete_last)
        self.ui.clearAll.clicked.connect(self.clear_all)

    def _construct_deleteAction(self):
        self.deleteAction = QAction("delete", self)
        self.deleteAction.setShortcut(QKeySequence.Delete)
        self.deleteAction.triggered.connect(self.delete_key)
        self.addAction(self.deleteAction)

    def _construct_okAction(self):
        self.okAction = QAction("OK", self)
        self.okAction.setShortcut(QKeySequence("Shift+Return"))
        self.okAction.triggered.connect(self.ok_action)
        self.addAction(self.okAction)

        self.ui.okButton.clicked.connect(self.ok)

    def _construct_backAction(self):
        self.ui.backButton.clicked.connect(self.back)

    def double_click(self, index):
        if index.column() in (0, 2):
            self.change_video(index.row())
        elif index.column() in (1, 3):
            self.change_question(index.row())

    def delete_key(self):
        fw = self.focusWidget()
        if fw is self.ui.videoList:
            self.delete_video()

    def find_last_row(self, item=''):
        end = self.list_model.rowCount()
        index = -1
        for i in reversed(range(0, end)):
            video = self.list_model.item(i, 0).text()
            question = self.list_model.item(i, 1).text()
            if item == 'video':
                text = video
            elif item == 'question':
                text = question
            elif item == 'video&question':
                text = video + question
            else:
                break
            if text == '':
                index = i
            else:
                break
        return index

    def add_item(self, video='', question='', index=-1):
        # Make Row Objects
        video_name = QtGui.QStandardItem(pathlib.Path(video).name)
        questions_name = QtGui.QStandardItem(pathlib.Path(question).name)
        videos = QtGui.QStandardItem(video)
        questions = QtGui.QStandardItem(question)

        # Row Settings
        video_name.setEditable(False)
        video_name.setDragEnabled(True)
        video_name.setDropEnabled(False)
        questions_name.setEditable(False)
        questions_name.setDropEnabled(False)
        videos.setEditable(False)
        videos.setDropEnabled(False)
        questions.setEditable(False)

        if index == -1:
            index = self.list_model.rowCount()
            self.list_model.appendRow(video_name)
        else:
            self.list_model.insertRow(index, video_name)
        self.list_model.setItem(index, 1, questions_name)
        self.list_model.setItem(index, 2, videos)
        self.list_model.setItem(index, 3, questions)

    def edit_item(self, index=None, video='', question=''):
        if index is None:
            item = ''
            if video != '' and question != '':
                item = 'video&question'
            elif video != '':
                item = 'video'
            elif question != '':
                item = 'question'
            index = self.find_last_row(item=item)

        videos_name = self.list_model.item(index, 0)
        questions_name = self.list_model.item(index, 1)
        videos = self.list_model.item(index, 2)
        questions = self.list_model.item(index, 3)

        if video != '':
            videos_name.setText(pathlib.Path(video).name)
            videos.setText(video)
        if question != '':
            questions_name.setText(pathlib.Path(question).name)
            questions.setText(question)

    def change_video(self, row):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            video_name = self.list_model.item(row, 0)
            videos = self.list_model.item(row, 2)
            v = dialog.selectedFiles()[0]
            video_name.setText(pathlib.Path(v).name)
            videos.setText(v)

    def change_question(self, row):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Question", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            questions_name = self.list_model.item(row, 1)
            questions = self.list_model.item(row, 3)
            q = dialog.selectedFiles()[0]
            questions_name.setText(pathlib.Path(q).name)
            questions.setText(q)

    def add_videos(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            video_names = dialog.selectedFiles()
            for video in video_names:
                last = self.find_last_row('video')
                if last == -1:
                    self.add_item(video=video)
                else:
                    self.edit_item(index=last, video=video)

    def add_questions(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Questions", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            question_names = dialog.selectedFiles()
            for question in question_names:
                last = self.find_last_row('question')
                if last == -1:
                    self.add_item(question=question)
                else:
                    self.edit_item(index=last, question=question)

    def video_directory(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video Directory", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            dir_names = dialog.selectedFiles()
            dir_path = pathlib.Path(dir_names[0])
            files = []
            for ext in self.v_types:
                files.extend(dir_path.glob(ext))
            for video in files:
                last = self.find_last_row('video')
                if last == -1:
                    self.add_item(video=str(video))
                else:
                    self.edit_item(index=last, video=str(video))

    def question_directory(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Questions Directory", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            dir_names = dialog.selectedFiles()
            dir_path = pathlib.Path(dir_names[0])
            files = []
            if len(self.q_types) < 1 or '*' in self.q_types:
                files = dir_path.iterdir()
            else:
                for ext in self.q_types:
                    files.extend(dir_path.glob(ext))
            for question in files:
                last = self.find_last_row('question')
                if last == -1:
                    self.add_item(question=str(question))
                else:
                    self.edit_item(index=last, question=str(question))

    def delete_last(self):
        last = self.list_model.rowCount() - 1
        self.list_model.removeRow(last)

    def delete_video(self):
        items = self.ui.videoList.selectedIndexes()
        indices = []
        for i in items:
            indices.append(i.row())
        indices.sort(reverse=True)
        for i in indices:
            self.list_model.removeRow(i)

    def clear_all(self):
        self.list_model.clear()
        self.list_model.setHorizontalHeaderLabels(self.header)
        self.ui.videoList.setColumnWidth(0, 200)
        self.ui.videoList.setColumnWidth(1, 200)
        self.ui.videoList.setColumnWidth(2, 100)
        self.ui.videoList.setColumnWidth(3, 100)

    def evaluate(self):
        self.subject.clear()
        self.session.clear()
        self.blocks.clear()
        self.subject.append(self.ui.subjectIDEdit.text())
        self.session.append(self.ui.blockEdit.text())
        for i in range(0, self.list_model.rowCount()):
            video = pathlib.Path(self.list_model.item(i, 2).text())
            question = pathlib.Path(self.list_model.item(i, 3).text())
            washout = self.ui.washoutBox.value()
            self.blocks.append({'video': video, 'questions': question, 'washout': washout})

    def ok(self):
        self.evaluate()
        self.ok_action()

    def default_ok(self):
        print("Not Connected")

    def back(self):
        self.back_action()

    def default_back(self):
        sys.exit()


class EmotionControl(WidgetContainer):
    def __init__(self, name="EmotionControl",  x_name="", events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.back_action = self.remove_from_stack
        self.experiment_name = x_name
        self._events = events

    @property
    def task_window(self):
        return self.widget.task_window

    @task_window.setter
    def task_window(self, value):
        self.widget.task_window = value

    @property
    def sequencer(self):
        return self.widget.sequencer

    @sequencer.setter
    def sequencer(self, value):
        self.widget.sequencer = value

    @property
    def block_widgets(self):
        return self.widget.block_widgets

    @block_widgets.setter
    def block_widgets(self, value):
        self.widget.block_widgets = value

    @property
    def sequence_order(self):
        return self.widget.sequence_order

    @sequence_order.setter
    def sequence_order(self, value):
        self.widget.sequence_order = value

    @property
    def player(self):
        return self.widget.player

    @player.setter
    def player(self, value):
        self.widget.player = value

    @property
    def parameters(self):
        return self.widget.paremeters

    @parameters.setter
    def parameters(self, value):
        self.widget.parameters = value

    @property
    def events(self):
        try:
            out = self.widget.events
        except AttributeError:
            out = self._events
        return out

    @events.setter
    def events(self, value):
        self._events = value
        if self.widget is not None:
            self.widget.events = value

    def construct_widget(self):
        self.widget = ControlWidget()
        self.widget.events = self._events
        self.widget.experiment_name = self.experiment_name

    def run(self, back_action=None):
        if back_action is not None:
            self.back_action = back_action

        self.widget.back_action = self.back_action
        self.widget.construct()
        self.widget.construct_blocks()
        super().run()


class ControlWidget(QWidget):
    header = ('Video', 'Questions', 'Washout', '')
    base_washout = 60

    def __init__(self, player=None, init=False, **kwargs):
        super().__init__(**kwargs)
        self.back_action = self.default_back
        self.start_action = self.default_start

        self.ui = Ui_EmotionControl()
        self.ui.setupUi(self)

        self.play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
        self.stop_icon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.skip_icon = self.style().standardIcon(QStyle.SP_MediaSkipForward)
        self.volume_icon = self.style().standardIcon(QStyle.SP_MediaVolume)
        self.mute_icon = self.style().standardIcon(QStyle.SP_MediaVolumeMuted)

        self._path = None
        self.subject = None
        self.session = None
        self.experiment_name = None
        self.events = None
        self.m_duration = 0
        self.mute = False

        self.task_window = None
        self.sequencer = None
        self._player = None
        self.media_player = None
        self.player = player

        self.parameters = None
        self.block_widgets = None
        self.block_sequence = -1
        self.sequence_order = []

        self.running = False
        self.blocks = None

        if init:
            self.construct()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        if value is not None:
            self.media_player = value.media_player

    def construct(self):
        self.subject = self.parameters['subject']
        self.session = self.parameters['session']
        self._construct_startAction()
        self._construct_backAction()
        self._construct_showAction()
        self._construct_fullScreenAction()
        self._construct_player_controls()
        self._construct_volume_controls()
        self.update_buttons(self.media_player.state())

    def construct_path(self):
        now = datetime.datetime.now().isoformat('_', 'seconds').replace(':', '~')
        file_name = self.parameters['subject'][0] + '_' + self.parameters['session'][0] + '_' + now + '.h5'
        return pathlib.Path(__file__).parent.joinpath(file_name)

    def construct_blocks(self):
        self.blocks = self.parameters['blocks']
        self._construct_queue()
        self.playing_model = QtGui.QStandardItemModel(0, 4)
        self.playing_model.setHorizontalHeaderLabels(self.header)
        self.ui.playingBlock.setModel(self.playing_model)
        self.ui.playingBlock.setColumnWidth(2, 75)
        self.ui.playingBlock.setColumnWidth(3, 25)
        self.complete_model = QtGui.QStandardItemModel(0, 4)
        self.complete_model.setHorizontalHeaderLabels(self.header)
        self.ui.completedBlocks.setModel(self.complete_model)
        # self.ui.completedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        # self.ui.completedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.completedBlocks.setColumnWidth(2, 75)
        self.ui.completedBlocks.setColumnWidth(3, 25)

    def _construct_queue(self):
        self.queue_model = QtGui.QStandardItemModel(0, 4)
        self.queue_model.setHorizontalHeaderLabels(self.header)
        self.ui.quequedBlocks.setModel(self.queue_model)
        # self.ui.quequedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        # self.ui.quequedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.quequedBlocks.setColumnWidth(2, 75)
        self.ui.quequedBlocks.setColumnWidth(3, 25)
        for i, block in enumerate(self.blocks):
            self.add_item(self.queue_model, _id=i, video=block['video'], washout=block['washout'])
        self.add_item(self.queue_model, _id=0, washout=self.base_washout)
        for i, block in enumerate(self.blocks):
            self.add_item(self.queue_model, _id=i, question=block['questions'])

    @staticmethod
    def add_item(model, _id=0, video=None, question=None, washout=0, index=-1):
        # Make Row Objects
        id_number = QtGui.QStandardItem(str(_id))
        if video is None or video == '':
            video_name = QtGui.QStandardItem('')
        else:
            video_name = QtGui.QStandardItem(pathlib.Path(video).name)
        if question is None or question == '':
            questions_name = QtGui.QStandardItem('')
        else:
            questions_name = QtGui.QStandardItem(pathlib.Path(question).name)
        if washout == 0:
            washout_name = QtGui.QStandardItem('')
        elif isinstance(washout, str):
            washout_name = QtGui.QStandardItem(washout)
        else:
            washout_name = QtGui.QStandardItem(str(washout) + "s")

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

    def _construct_startAction(self):
        self.ui.startButton.clicked.connect(self.start)

    def _construct_backAction(self):
        self.ui.backButton.clicked.connect(self.back)

    def _construct_showAction(self):
        self.ui.showButton.clicked.connect(self.task_window.show)

    def _construct_fullScreenAction(self):
        self.ui.fullscreenButton.clicked.connect(self.task_window.fullscreen_action)

    def _construct_player_controls(self):
        self.media_player.durationChanged.connect(self.duration_change)
        self.media_player.positionChanged.connect(self.position_change)
        self.media_player.stateChanged.connect(self.update_buttons)
        self.ui.playButton.setIcon(self.play_icon)
        self.ui.stopButton.setIcon(self.stop_icon)
        self.ui.stopButton.clicked.connect(self.media_player.stop)
        self.ui.skipButton.setIcon(self.skip_icon)
        self.ui.skipButton.clicked.connect(self.skip_action)

    def _construct_volume_controls(self):
        self.media_player.stateChanged.connect(self.update_buttons)
        self.ui.muteButton.setIcon(self.volume_icon)
        self.ui.muteButton.clicked.connect(self.mute_action)
        self.mute = False

        self.ui.volumeSlider.setValue(self.media_player.volume())
        self.ui.volumeSlider.valueChanged.connect(self.media_player.setVolume)

    def update_buttons(self, state):
        self.ui.stopButton.setEnabled(state != QtMultimedia.QMediaPlayer.StoppedState)
        if state == QtMultimedia.QMediaPlayer.PlayingState:
            self.ui.playButton.clicked.connect(self.media_player.pause)
            self.ui.playButton.setIcon(self.pause_icon)
        elif state != QtMultimedia.QMediaPlayer.PlayingState:
            self.ui.playButton.clicked.connect(self.media_player.play)
            self.ui.playButton.setIcon(self.play_icon)

    def duration_change(self, dur):
        self.m_duration = dur / 1000
        self.ui.durationSlider.setMaximum(self.m_duration)

    def position_change(self, progress):
        if not self.ui.durationSlider.isSliderDown():
            self.ui.durationSlider.setValue(progress / 1000)
        self.set_duration_label(progress / 1000)

    def set_duration_label(self, progress):
        pos = str(int(progress // 60)) + ':' + str(progress % 60)
        total_dur = str(int(self.m_duration // 60)) + ':' + str(self.m_duration % 60)
        self.ui.durationLabel.setText(pos + ' / ' + total_dur)

    def mute_action(self):
        if self.mute:
            self.mute = False
            self.ui.muteButton.setIcon(self.volume_icon)
        else:
            self.mute = True
            self.ui.muteButton.setIcon(self.mute_icon)
        self.media_player.setMuted(self.mute)

    def skip_action(self):
        self.media_player.stop()
        video = self.block_widgets['video_player'].video
        if isinstance(video, pathlib.Path):
            video = video.name
        event = {"type_": 'Skip', 'Video': video}
        while self.sequencer.next_index() != 0:
            self.sequencer.skip()
        self.advance_block(event=event)

    def start_sequence(self):
        self.sequencer.clear()
        block = self.blocks[0]
        block_sequence = self.sequence_order.index('*block*')
        sequence_order = self.sequence_order[:block_sequence]

        if len(sequence_order) > 1:
            first = sequence_order.pop(0)
            self.sequencer.insert(self.block_widgets[first], ok_action=self.advance, back_action=self.task_window.hide)
        last = sequence_order.pop()
        for item in sequence_order:
            self.sequencer.insert(self.block_widgets[item], ok_action=self.advance)
        self.sequencer.insert(self.block_widgets[last], ok_action=self.advance)
        self.sequencer.insert(self.block_widgets['washout'], milliseconds=(self.base_washout-block['washout']) * 1000, timer_action=self.advance_block)

    def end_sequence(self):
        block = self.blocks[-1]
        block_sequence = self.sequence_order.index('*block*')
        sequence_order = self.sequence_order[block_sequence + 1:]

        self.sequencer.insert(self.block_widgets['finish'])

    def next_queue(self):
        if self.playing_model.rowCount() > 0:
            complete_index = int(self.playing_model.item(0, 3).text())
            video = self.playing_model.item(0, 0).text()
            question = self.playing_model.item(0, 1).text()
            washout = self.playing_model.item(0, 2).text()
            self.playing_model.item(0, 3).text()
            self.add_item(self.complete_model, _id=complete_index, video=video, question=question, washout=washout)

        self.playing_model.clear()
        self.playing_model.setHorizontalHeaderLabels(self.header)
        if self.queue_model.rowCount() > 0:
            play_index = int(self.queue_model.item(0, 3).text())
            video = self.queue_model.item(0, 0).text()
            question = self.queue_model.item(0, 1).text()
            washout = self.queue_model.item(0, 2).text()

            self.add_item(self.playing_model, _id=play_index, video=video, question=question, washout=washout)
            self.queue_model.removeRow(0)
            flag = True
        else:
            flag = False

        return flag

    def next_block(self):
        play_index = int(self.playing_model.item(0, 3).text())
        video = self.playing_model.item(0, 0).text()
        questions = self.playing_model.item(0, 1).text()
        washout = self.playing_model.item(0, 2).text()
        block = self.blocks[play_index]

        if video != '':
            if block['washout'] > 0:
                self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000, timer_action=self.advance)
            self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance_block)
        elif questions != '':
            self.sequencer.insert(self.block_widgets['questionnaire'], path=block['questions'], finish_action=self.advance_block)
        elif washout != '':
            self.sequencer.insert(self.block_widgets['washout'], milliseconds=self.base_washout * 1000, timer_action=self.advance_block)

    def advance(self, event=None, caller=None):
        self.events.append(**event)
        next(self.sequencer)

    def advance_block(self, event=None, caller=None):
        more_blocks = self.next_queue()
        if more_blocks:
            self.next_block()
        else:
            self.end_sequence()
        self.advance(event=event, caller=caller)

    def start(self):
        if self.running:
            self.running_action(caller=self)
        else:
            self.running = True
            self.start_action(caller=self)

    def default_start(self, caller=None):
        self.events.path = self.construct_path()
        self.events.construct()
        self.events.Subject = self.subject
        self.events.Task = self.experiment_name
        self.events.Block = self.session
        self.events.open()
        self.events.set_time()
        self.start_sequence()
        self.ui.startButton.setEnabled(False)
        self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionControl", 'Stop', None, -1))
        self.sequencer.start()
        self.task_window.show()

    def running_action(self, caller=None):
        pass

    def back(self):
        if self.running:
            self.stop()
        else:
            self.back_action()

    def default_back(self, caller=None):
        sys.exit()

    def stop(self):
        if self.running:
            self.media_player.stop()
            self.sequencer.clear()
            event = {"type_": 'ManualStop'}
            self.events.append(**event)
            self.running = False
            self.reset()
            self.ui.startButton.setEnabled(True)
            self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionControl", 'Back', None, -1))

    def reset(self):
        if not self.running:
            self.events.clear()
            self.sequencer.clear()
            self.complete_model.clear()
            self.queue_model.clear()
            self.playing_model.clear()
            self.complete_model.setHorizontalHeaderLabels(self.header)
            self.queue_model.setHorizontalHeaderLabels(self.header)
            self.playing_model.setHorizontalHeaderLabels(self.header)
            for i, block in enumerate(self.blocks):
                self.add_item(self.queue_model, _id=i, video=block['video'], washout=block['washout'])
            self.add_item(self.queue_model, _id=0, washout=self.base_washout)
            for i, block in enumerate(self.blocks):
                self.add_item(self.queue_model, _id=i, question=block['questions'])
