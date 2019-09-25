"""
.py

Last Edited:

Lead Author[s]: Anthony Fong
Contributor[s]:

Description:


Machine I/O
Input:
Output:

User I/O
Input:
Output:


"""
########################################################################################################################

########## Libraries, Imports, & Setup ##########

# Default Libraries #
import sys
from abc import ABC, abstractmethod
import pathlib
import copy
import datetime
import time # use perf_counter

# Downloaded Libraries #
from bidict import bidict
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtCore import Slot, Signal, QObject, QDir
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Libraries #
from QtUtility.stackedwindow import WidgetStack
from emotionTask.UI.emotionparameters import Ui_EmotionParameters
from emotionTask.UI.emotioninstructions import Ui_EmotionInstructions
from emotionTask.UI.emotionwashout import Ui_EmotionWashout
from emotionTask.UI.emotionvideoplayer import Ui_EmotionVideoPlayer
from emotionTask.UI.emotioncontrol import Ui_EmotionControl


########## Definitions ##########

# Classes #
class EmotionTask:
    def __init__(self, parent=None, stack=None, r_widget=None):
        self.parent = parent
        self.widget_stack = stack
        self.return_widget = r_widget

        self.task_window = TaskWindow()
        self.events = EventLogger()
        
        self.sequencer = WidgetContainerSequencer()
        self.task_window.sequencer = self.sequencer

        self.parameters = EmotionParameters()
        self.control = EmotionControl(events=self.events)
        self.instructions = EmotionInstructions(events=self.events)
        self.video_player = EmotionVideoPlayer(events=self.events)
        self.questionnaire = None
        self.washout = EmotionWashout(events=self.events)
        self.finished = None

        self.block_widgets = {'instructions': self.instructions, 'video_player': self.video_player,
                              'questionnaire': self.questionnaire, 'washout': self.washout, 'finished': self.finished}
        self.sequence_order = ['instructions', '*block*', 'finished']
        self.block_order = ['video_player', 'questionnaire', 'washout']

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

    def setup_task(self):
        self.parameters.run(self.control_task, self.unload_task)

    def control_task(self):
        self.control.run(self.parameters.run)


class WidgetContainerSequencer:
    def __init__(self):
        self.index = None
        self.sequence = []
        self.loop = False

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.loop and self.index >= len(self.sequence):
            raise StopIteration
        return self.preincrement()

    def insert(self, widget, index=None, **kwargs):
        if index is None:
            self.sequence.append({"widget": widget, "kwargs": kwargs})
            return len(self.sequence)
        else:
            self.sequence.insert(index, {"widget": widget, "kwargs": kwargs})
            return index

    def remove(self, index):
        del self.sequence[index]

    def pop(self, index=-1):
        return self.sequence.pop(index)

    def clear(self):
        self.sequence.clear()
        self.index = None

    def next_index(self):
        if isinstance(self.index, int) and self.index + 1 < len(self.sequence):
            return self.index + 1
        else:
            return 0

    def current(self):
        info = self.sequence[self.index]
        return info["widget"], info["kwargs"], self.index

    def next(self):
        info = self.sequence[self.next_index()]
        return info["widget"], info["kwargs"], self.next_index()

    def increment_index(self):
        self.index = self.next_index()

    def run_current(self):
        widget = self.sequence[self.index]["widget"]
        kwargs = self.sequence[self.index]["kwargs"]
        return widget.run(**kwargs)

    def start(self):
        self.index = 0
        return self.run_current()

    def reset(self):
        self.index = None

    def preincrement(self):
        self.index = self.next_index()
        return self.run_current()

    def postincrement(self):
        output = self.run_current()
        self.index = self.next_index()
        return output


class TaskWindow(WidgetStack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sequencer = None

        self.fullscreenAction = QAction("FullScreen", self)
        self.fullscreenAction.setShortcut(QKeySequence.FullScreen)
        self.fullscreenAction.triggered.connect(self.fullscreen_action)
        self.addAction(self.fullscreenAction)

    def fullscreen_action(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


class WidgetContainer(ABC):
    def __init__(self, name="", init=False):
        self.name = name

        self.widget = None
        self.widget_stack = None
        self.return_widget = None

        if init:
            self.construct_widget()

    @abstractmethod
    def construct_widget(self):
        self.widget = None

    def destroy_widget(self):
        self.widget = None

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.construct_widget()
        if stack is not None:
            self.widget_stack = stack
        if name is None:
            name = self.name

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.widget_stack.add(self.widget, name)

    def remove_from_stack(self, stack=None, back=True, clear_widget=False):
        if stack is not None:
            self.widget_stack = stack
        if back:
            self.widget_stack.set(self.return_widget)

        self.widget_stack.remove(self.name)

        if clear_widget:
            self.widget = None

    def make_active(self):
        self.widget_stack.set(self.name)

    def run(self):
        self.widget_stack.set(self.name)


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
    q_types = ('*.txt',)

    def __init__(self):
        super(ParametersWidget, self).__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self._parameters = {}
        self.blocks = []
        self.loops = None
        self.randomize = None

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
        self._parameters['blocks'] = self.blocks
        self._parameters['loops'] = self.loops
        self._parameters['randomize'] = self.randomize
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
                return i
        return -1

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
        dialog = QFileDialog(self, caption="Open Video", directory=QDir.homePath())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            video_name = self.list_model.item(row, 0)
            videos = self.list_model.item(row, 2)
            v = dialog.selectedFiles()[0]
            video_name.setText(pathlib.Path(v).name)
            videos.setText(v)

    def change_question(self, row):
        dialog = QFileDialog(self, caption="Open Question", directory=QDir.homePath())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            questions_name = self.list_model.item(row, 1)
            questions = self.list_model.item(row, 3)
            q = dialog.selectedFiles()[0]
            questions_name.setText(pathlib.Path(q).name)
            questions.setText(q)

    def add_videos(self):
        dialog = QFileDialog(self, caption="Open Video", directory=QDir.homePath())
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
        dialog = QFileDialog(self, caption="Open Questions", directory=QDir.homePath())
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
        dialog = QFileDialog(self, caption="Open Video Directory", directory=QDir.homePath())
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
        dialog = QFileDialog(self, caption="Open Questions Directory", directory=QDir.homePath())
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            dir_names = dialog.selectedFiles()
            dir_path = pathlib.Path(dir_names[0])
            files = []
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
        self.randomize = self.ui.randomizeVideosBox.isChecked()
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
    def __init__(self, name="EmotionControl", events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.back_action = self.remove_from_stack
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

    def run(self, back_action=None):
        if back_action is not None:
            self.back_action = back_action

        self.widget.back_action = self.back_action
        self.widget.construct()
        self.widget.construct_blocks()
        super().run()


class ControlWidget(QWidget):
    header = ('Video', 'Questions', 'Washout', '')

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

        self.blocks = None

        if init:
            self.construct()

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        if value is not None:
            self.media_player = value.media_player

    def construct(self):
        self._construct_startAction()
        self._construct_backAction()
        self._construct_showAction()
        self._construct_fullScreenAction()
        self._construct_player_controls()
        self._construct_volume_controls()
        self.update_buttons(self.media_player.state())

    def construct_blocks(self):
        self.blocks = self.parameters['blocks']
        self._construct_queue()
        self.playing_model = QtGui.QStandardItemModel(0, 4)
        self.playing_model.setHorizontalHeaderLabels(self.header)
        self.ui.playingBlock.setModel(self.playing_model)
        self.complete_model = QtGui.QStandardItemModel(0, 4)
        self.complete_model.setHorizontalHeaderLabels(self.header)
        self.ui.completedBlocks.setModel(self.complete_model)
        self.ui.completedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        self.ui.completedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        self.start_sequence()

    def _construct_queue(self):
        self.queue_model = QtGui.QStandardItemModel(0, 4)
        self.queue_model.setHorizontalHeaderLabels(self.header)
        self.ui.quequedBlocks.setModel(self.queue_model)
        self.ui.quequedBlocks.setDragDropMode(QAbstractItemView.InternalMove)
        self.ui.quequedBlocks.setSelectionMode(QAbstractItemView.MultiSelection)
        for i, block in enumerate(self.blocks):
            self.add_item(self.queue_model, _id=i, video=block['video'], question=block['questions'], washout=block['washout'])

    @staticmethod
    def add_item(model, _id=0, video=pathlib.Path, question=pathlib.Path, washout=0, index=-1):
        # Make Row Objects
        id_number = QtGui.QStandardItem(str(_id))
        video_name = QtGui.QStandardItem(video.name)
        questions_name = QtGui.QStandardItem(question.name)
        washout_name = QtGui.QStandardItem(str(washout)+"s")

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
            self.ui.durationSlider.setValue(progress/1000)
        self.set_duration_label(progress/1000)

    def set_duration_label(self, progress):
        pos = str(int(progress//60))+':'+str(progress % 60)
        total_dur = str(int(self.m_duration//60))+':'+str(self.m_duration % 60)
        self.ui.durationLabel.setText(pos+' / '+total_dur)

    def mute_action(self):
        if self.mute:
            self.mute = False
            self.ui.muteButton.setIcon(self.volume_icon)
        else:
            self.mute = True
            self.ui.muteButton.setIcon(self.mute_icon)
        self.media_player.setMuted(self.mute)

    def skip_action(self):
        pass

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
        block_sequence = self.sequence_order.index('*block*')
        sequence_order = self.sequence_order[block_sequence+1:]

        last = sequence_order.pop()
        for item in sequence_order:
            self.sequencer.insert(self.block_widgets[item], ok_action=self.advance)
        self.sequencer.insert(self.block_widgets[last], return_action=self.setup_task)

    def next_queue(self):
        if self.playing_model.rowCount() > 0:
            complete_index = int(self.playing_model.item(0, 3).text())
            complete = self.blocks[complete_index]
            self.add_item(self.complete_model, _id=complete_index, video=complete['video'], question=complete['questions'], washout=complete['washout'])

        self.playing_model.clear()
        self.playing_model.setHorizontalHeaderLabels(self.header)
        if self.queue_model.rowCount() > 0:
            play_index = int(self.queue_model.item(0, 3).text())
            block = self.blocks[play_index]

            self.add_item(self.playing_model, _id=play_index, video=block['video'], question=block['questions'], washout=block['washout'])
            self.queue_model.removeRow(0)
            flag = True
        else:
            flag = False

        return flag

    def next_block(self):
        play_index = int(self.playing_model.item(0, 3).text())
        block = self.blocks[play_index]

        self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance)
        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout']*1000, timer_action=self.advance_block)

    def advance(self, event=None, caller=None):
        self.events.append(**event)
        next(self.sequencer)

    def advance_block(self, event=None, caller=None):
        more_blocks = self.next_queue()
        if more_blocks:
            self.next_block()
        else:
            pass  # self.end_sequence()
        self.advance(event=event, caller=caller)

    def start(self):
        self.start_action(caller=self)

    def default_start(self, caller=None):
        self.sequencer.start()
        self.task_window.show()
        self.events.set_time()

    def back(self):
        self.back_action(caller=self)

    def default_back(self, caller=None):
        sys.exit()


class EmotionInstructions(WidgetContainer):
    def __init__(self, name="Instructions", path=None, events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack
        
        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path.cwd().joinpath('emotionTask', 'instructions.txt')
        else:
            self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def construct_widget(self):
        self.widget = InstructionsWidget()

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        self.load_text()
        super().run()

    def load_text(self):
        with self.path.open('r') as file:
            self.widget.text = file.read()
        self.widget.set_text()


class InstructionsWidget(QWidget):
    def __init__(self):
        super(InstructionsWidget, self).__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self.ui = Ui_EmotionInstructions()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.ok)
        self.ui.backButton.clicked.connect(self.back)

        self.okAction = QAction("OK", self)
        self.okAction.setShortcut(QKeySequence("Shift+Return"))
        self.okAction.triggered.connect(self.ok_action)
        self.addAction(self.okAction)

        self.text = None

    def set_text(self, text=None):
        if text is not None:
            self.text = text
        self.ui.textBrowser.setText(self.text)

    def ok(self):
        event = {'_type': 'Instructions', 'Accepted': True}
        self.ok_action(event=event, caller=self)

    def default_ok(self, event=None, caller=None):
        print("Not Connected")

    def back(self):
        event = {'_type': 'Instructions', 'Accepted': False}
        self.back_action(event=event, caller=self)

    def default_back(self, event=None, caller=None):
        sys.exit()


class EmotionWashout(WidgetContainer):
    def __init__(self, name="Washout", events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.timer_action = None
        
        self.events = events

        self.milliseconds = 0
        self.font_size = 100
        self.text = "X"

    def construct_widget(self):
        self.widget = WashoutWidget()

    def run(self, milliseconds=None, timer_action=None):
        if milliseconds is not None:
            self.milliseconds = milliseconds
        if timer_action is not None:
            self.timer_action = timer_action

        self.widget.timer_action = self.timer_action
        self.widget.milliseconds = self.milliseconds
        super().run()
        self.widget.start()

    def setup(self):
        self.widget.milliseconds = self.milliseconds
        self.widget.set_text(self.text)
        self.widget.set_font_size(self.font_size)


class WashoutWidget(QWidget):
    def __init__(self):
        super(WashoutWidget, self).__init__()
        self.timer_action = self.default_timer_action

        self.ui = Ui_EmotionWashout()
        self.ui.setupUi(self)

        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)
        self.milliseconds = 0

    def set_text(self, t):
        self.ui.label.setText(t)

    def set_font_size(self, s):
        font = self.ui.label.font()
        font.setPointSize(s)
        self.ui.label.setFont(font)

    def start(self, washout_length=None):
        if washout_length is not None:
            self.milliseconds = washout_length
        self.timer.start(self.milliseconds)

    def timeout(self):
        event = {'_type': 'WashoutFinished', 'duration': self.milliseconds/1000}
        self.timer_action(event=event, caller=self)

    def default_timer_action(self, event=None, caller=None):
        print("Time is up!")


class EmotionVideoPlayer(WidgetContainer):
    def __init__(self, name="VideoPlayer", source="path", path=None, url=None, events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self._frame_action = self.frame_process
        self._finish_action = None
        
        self.events = events
        
        self._media_player = None
        self.source = source
        
        self._path = None
        if path is None:
            self._path = pathlib.Path.cwd().joinpath('emotionTask', 'instructions.mp4')
        else:
            self.path = path

        self._url = None
        if url is None:
            self._url = QtCore.QUrl("http://clips.vorwaerts-gmbh.de/VfE_html5.mp4")
        else:
            self.url = url

    @property
    def media_player(self):
        try:
            out = self.widget.mediaPlayer
        except AttributeError:
            out = self._media_player
        return out

    @media_player.setter
    def media_player(self, value):
        self._media_player = value
        if self.widget is not None:
            self.widget.mediaPlayer = value

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
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if isinstance(value, QtCore.QUrl) or value is None:
            self._url = value
        else:
            self._url = QtCore.QUrl(value)

    @property
    def video(self):
        if self.source is "url":
            return self._url
        else:
            return self._path

    @property
    def frame_action(self):
        try:
            out = self.widget.frame_action
        except AttributeError:
            out = self._frame_action
        return out

    @frame_action.setter
    def frame_action(self, value):
        self._frame_action = value
        if self.widget is not None:
            self.widget.frame_action = value

    @property
    def finish_action(self):
        try:
            out = self.widget.finish_action
        except AttributeError:
            out = self._finish_action
        return out

    @finish_action.setter
    def finish_action(self, value):
        self._finish_action = value
        if self.widget is not None:
            self.widget.finish_action = value

    def construct_widget(self):
        self.widget = VideoPlayerWidget()
        self.widget.frame_action = self._frame_action
        self.widget.finish_action = self._finish_action

    def run(self, source="path", path=None, url=None, frame_action=None, finish_action=None):
        if source is not None:
            self.source = source
        if path is not None:
            self.path = path
        if url is not None:
            self.url = url
        if frame_action is not None:
            self.frame_action = frame_action
        if finish_action is not None:
            self.finish_action = finish_action

        self.load_video()
        super().run()
        self.widget.play()

    def load_video(self, video=None):
        if video is None:
            self.widget.set_video(self.video)
        else:
            self.widget.set_video(video)

    def frame_process(self, frame=None, number=None, event=None, caller=None):
        # could use frame metadata if is exists: print(frame.metaData(str_name))
        self.events.append('Frame', video=self.video, frame=number)
        print(self.events[-1])


class VideoPlayerWidget(QWidget):
    def __init__(self, frame_action=None, **kwargs):
        super(VideoPlayerWidget, self).__init__(**kwargs)
        if frame_action is None:
            self.frame_action = self.default_frame
        else:
            self.frame_action = frame_action
        self.finish_action = self.default_finish

        self.ui = Ui_EmotionVideoPlayer()
        self.ui.setupUi(self)

        self.ui.videoPlayer = QtMultimediaWidgets.QVideoWidget()
        self.ui.gridLayout.addWidget(self.ui.videoPlayer, 0, 0, 1, 1)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
        self.video_item = QtMultimediaWidgets.QGraphicsVideoItem()
        self.mediaPlayer.setVideoOutput(self.ui.videoPlayer)
        self.mediaPlayer.mediaStatusChanged.connect(self.status_check)

        self.frameProbe = QtMultimedia.QVideoProbe(self)
        self.frameProbe.videoFrameProbed.connect(self.frame)
        self.frameProbe.setSource(self.mediaPlayer)
        self.frame_number = 0

        self.video = None

    def set_video(self, video):
        self.video = video
        if isinstance(video, pathlib.Path) or isinstance(video, str):
            video = QtCore.QUrl.fromLocalFile(str(video))
        if isinstance(video, QtCore.QUrl):
            video = QtMultimedia.QMediaContent(video)
        self.mediaPlayer.setMedia(video)
        self.frame_number = 0

    def play(self):
        self.mediaPlayer.play()

    def frame(self, frame):
        self.frame_number += 1
        event = {'_type': 'Frame', 'video': self.video, 'frame': self.frame_number}
        self.frame_action(frame, self.frame_number, event=event, caller=self)

    def default_frame(self, frame=None, number=None, event=None, caller=None):
        print(QtCore.QTime.currentTime().toString("hh:mm:ss.zzzz"))

    def status_check(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.finish()

    def finish(self):
        event = {'_type': 'VideoFinished', 'video': self.video}
        self.finish_action(event=event, caller=self)

    def default_finish(self, event=None, caller=None):
        print("Done!")


import collections


class EventLogger(collections.UserList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_datetime = None
        self.start_time_counter = None

    def set_time(self):
        self.start_datetime = datetime.datetime.now()
        self.start_time_counter = time.perf_counter()
        self.append({'Time': self.start_datetime, 'DeltaTime': 0, 'Type': 'TimeSet'})

    def create_event(self,  _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {'Time': now, 'DeltaTime': seconds, 'Type': _type, **kwargs}

    def append(self, _type, **kwargs):
        if isinstance(_type, dict):
            super().append(_type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().append(event)

    def insert(self, i, _type, **kwargs):
        if isinstance(_type, dict):
            super().insert(i, _type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().insert(i, event)
