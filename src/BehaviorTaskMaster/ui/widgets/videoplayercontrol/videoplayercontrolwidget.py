""" videoplayercontrolwidget.py
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
import datetime

# Third-Party Packages #
from PySide2 import QtGui, QtWidgets, QtMultimedia
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Packages #
from .videoplayercontrol import Ui_VideoPlayerControl


# Definitions #
# Classes #
class VideoPlayerControlWidget(QWidget):
    header = ('Video', 'Questions', 'Washout', '')
    base_washout = 60
    default_washout = 0

    def __init__(self, player=None, init=False, **kwargs):
        super().__init__(**kwargs)
        self.back_action = self.default_back
        self.start_action = self.default_start

        self.ui = Ui_VideoPlayerControl()
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
        self.subject = self.parameters['subject'][0]
        self.session = self.parameters['session'][0]
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
        columns = len(self.header)
        self.queue_model = QtGui.QStandardItemModel(0, columns)
        self.queue_model.setHorizontalHeaderLabels(self.header)
        self.ui.quequedBlocks.setModel(self.queue_model)
        # self.ui.quequedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        # self.ui.quequedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.quequedBlocks.setColumnWidth(2, 75)
        self.ui.quequedBlocks.setColumnWidth(3, 25)
        self.blocks = self.parameters['blocks']

        self._fill_queue()

        self.playing_model = QtGui.QStandardItemModel(0, columns)
        self.playing_model.setHorizontalHeaderLabels(self.header)
        self.ui.playingBlock.setModel(self.playing_model)
        self.ui.playingBlock.setColumnWidth(2, 75)
        self.ui.playingBlock.setColumnWidth(3, 25)

        self.complete_model = QtGui.QStandardItemModel(0, columns)
        self.complete_model.setHorizontalHeaderLabels(self.header)
        self.ui.completedBlocks.setModel(self.complete_model)
        # self.ui.completedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        # self.ui.completedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.completedBlocks.setColumnWidth(2, 75)
        self.ui.completedBlocks.setColumnWidth(3, 25)

    def _fill_queue(self):
        for i, block in enumerate(self.blocks):
            self.add_item(self.queue_model, _id=i, **block)

    def add_item(self, model, _id=0, index=-1, video=None, configuration=None, washout=None, **kwargs):
        # Make Row Objects
        id_number = QtGui.QStandardItem(str(_id))
        if video is None or video == '':
            video_name = QtGui.QStandardItem('')
        else:
            video_name = QtGui.QStandardItem(pathlib.Path(video).name)

        if configuration is None or configuration == '':
            questions_name = QtGui.QStandardItem('')
        else:
            questions_name = QtGui.QStandardItem(pathlib.Path(configuration).name)

        if washout is None or washout == '':
            washout = self.default_washout
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

        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000, timer_action=self.advance)
        self.sequencer.insert(self.block_widgets['finish'])

    def next_queue(self):
        if self.playing_model.rowCount() > 0:
            complete_index = int(self.playing_model.item(0, 3).text())
            complete = self.blocks[complete_index]
            self.add_item(self.complete_model, _id=complete_index, **complete)

        self.playing_model.clear()
        self.playing_model.setHorizontalHeaderLabels(self.header)
        if self.queue_model.rowCount() > 0:
            play_index = int(self.queue_model.item(0, 3).text())
            block = self.blocks[play_index]

            self.add_item(self.playing_model, _id=play_index, **block)
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

        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000, timer_action=self.advance)
        # self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance_trigger)
        self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance)
        self.sequencer.insert(self.block_widgets['questionnaire'], path=block['configuration'], finish_action=self.advance_block)

    def advance(self, event=None, caller=None):
        self.events.append(**event)
        next(self.sequencer)

    def advance_trigger(self, event=None, caller=None):
        event = {'SubType': event["type_"]}
        self.events.trigger_event(**event)
        next(self.sequencer)

    def advance_block(self, event=None, caller=None):
        more_blocks = self.next_queue()
        if more_blocks:
            self.next_block()
        else:
            self.end_sequence()
        self.advance(event=event, caller=caller)

    def advance_block_trigger(self, event=None, caller=None):
        more_blocks = self.next_queue()
        if more_blocks:
            self.next_block()
        else:
            self.end_sequence()
        self.advance_trigger(event=event, caller=caller)

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
        self.ui.backButton.setText(QtWidgets.QApplication.translate("VideoPlayerControl", 'Stop', None, -1))
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
            self.ui.backButton.setText(QtWidgets.QApplication.translate("VideoPlayerControl", 'Back', None, -1))

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
            self._fill_queue()
