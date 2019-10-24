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

# Downloaded Libraries #
from bidict import bidict
from bidict import frozenbidict
import toml
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtCore import QDir
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Libraries #
from QtUtility.stackedwindow import WidgetStack
from emotionTasks.UI.emotionparameters import Ui_EmotionParameters
from emotionTasks.UI.emotioninstructions import Ui_EmotionInstructions
from emotionTasks.UI.emotionwashout import Ui_EmotionWashout
from emotionTasks.UI.emotionquestionnaire import Ui_EmotionQuestionnaire
from emotionTasks.UI.emotionvideoplayer import Ui_EmotionVideoPlayer
from emotionTasks.UI.emotioncontrol import Ui_EmotionControl
from emotionTasks.UI.emotionfinish import Ui_EmotionFinish


########## Definitions ##########

# Classes #
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

    def skip(self):
        self.index = self.next_index()
        return self.index


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

    def remove_from_stack(self, stack=None, back=True, clear_widget=False, **kwargs):
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

        self._path = None
        self.subject = None
        self.session = None
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
        file_name = self.parameters['subject'][0] + '_' + self.parameters['session'][0] + '_' + now + '.csv'
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
            self.add_item(self.queue_model, _id=i, video=block['video'], question=block['questions'],
                          washout=block['washout'])

    @staticmethod
    def add_item(model, _id=0, video=pathlib.Path, question=pathlib.Path, washout=0, index=-1):
        # Make Row Objects
        id_number = QtGui.QStandardItem(str(_id))
        video_name = QtGui.QStandardItem(video.name)
        questions_name = QtGui.QStandardItem(question.name)
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
        event = {'_type': 'Skip', 'Video': video}
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

        self.sequencer.insert(self.block_widgets['washout'], milliseconds=block['washout'] * 1000,
                              timer_action=self.advance)
        self.sequencer.insert(self.block_widgets['finish'])

    def next_queue(self):
        if self.playing_model.rowCount() > 0:
            complete_index = int(self.playing_model.item(0, 3).text())
            complete = self.blocks[complete_index]
            self.add_item(self.complete_model, _id=complete_index, video=complete['video'],
                          question=complete['questions'], washout=complete['washout'])

        self.playing_model.clear()
        self.playing_model.setHorizontalHeaderLabels(self.header)
        if self.queue_model.rowCount() > 0:
            play_index = int(self.queue_model.item(0, 3).text())
            block = self.blocks[play_index]

            self.add_item(self.playing_model, _id=play_index, video=block['video'], question=block['questions'],
                          washout=block['washout'])
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
        self.sequencer.insert(self.block_widgets['video_player'], path=block['video'], finish_action=self.advance)
        self.sequencer.insert(self.block_widgets['questionnaire'], path=block['questions'],
                              finish_action=self.advance_block)

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
        self.events.set_time()
        self.start_sequence()
        self.ui.startButton.setEnabled(False)
        self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionControl", 'Stop', None, -1))
        self.sequencer.start()
        self.task_window.show()
        self.events.path = self.construct_path()

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
            event = {'_type': 'ManualStop'}
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
                self.add_item(self.queue_model, _id=i, video=block['video'], question=block['questions'],
                              washout=block['washout'])


class InstructionsWidget(QWidget):
    def __init__(self):
        super().__init__()
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
        self.color = 'rgb' + str((224, 224, 224))

        self.ui.colorSpacer.setStyleSheet('background-color:' + self.color)

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
        event = {'_type': 'Washout', 'SubType': 'Finished', 'Duration': self.milliseconds / 1000}
        self.timer_action(event=event, caller=self)

    def default_timer_action(self, event=None, caller=None):
        print("Time is up!")


class QuestionnaireWidget(QWidget):
    number_key = frozenbidict({0: QtCore.Qt.Key_0, 1: QtCore.Qt.Key_1, 2: QtCore.Qt.Key_2, 3: QtCore.Qt.Key_3,
                               4: QtCore.Qt.Key_4, 5: QtCore.Qt.Key_5, 6: QtCore.Qt.Key_6, 7: QtCore.Qt.Key_7,
                               8: QtCore.Qt.Key_8, 9: QtCore.Qt.Key_9})

    def __init__(self, next_action=None, finish_action=None, previous_action=None, back_action=None, answer_action=None,
                 **kwargs):
        super().__init__(**kwargs)
        if next_action is None:
            self.next_action = self.default_next
        else:
            self.next_action = next_action
        if finish_action is None:
            self.finish_action = self.default_finish
        else:
            self.finish_action = finish_action
        if previous_action is None:
            self.previous_action = self.default_previous
        else:
            self.previous_action = previous_action
        if back_action is None:
            self.back_action = self.default_back
        else:
            self.back_action = back_action
        if answer_action is None:
            self.answer_action = self.default_answer
        else:
            self.answer_action = answer_action

        self.ui = Ui_EmotionQuestionnaire()
        self.ui.setupUi(self)

        self.ui.continueButton.clicked.connect(self._continue)
        self.ui.backButton.clicked.connect(self.previous)

        self.continueAction = QAction("Continue", self)
        self.continueAction.setShortcut(QKeySequence("Shift+Return"))
        self.continueAction.triggered.connect(self._continue)
        self.addAction(self.continueAction)

        self._path = None
        self.text = None
        self.qa = []
        self.answers = []
        self.answer_key = bidict()
        self.q_index = 0

        self.multi_answers = 1
        self.current_question = None
        self.current_answers = None
        self.current_color = None
        self.selected_answer = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def load_file(self, file):
        if file is not None:
            self.path = file
        if self.path.as_posix() != '.':
            q_file = toml.load(self.path)
            self.qa = q_file['Questions']
            self.q_index = 0
            qa = self.qa[self.q_index]
            self.set_color(qa['color'])
            self.set_question(qa['question'])
            self.set_answers(qa['answers'], qa['format'])

    def set_color(self, color):
        if color is not None:
            self.ui.colorSpacer.setStyleSheet('background-color:rgb(' + color + ')')
            self.current_color = color

    def set_question(self, question):
        self.ui.questionBrowser.setText(question)
        self.current_question = question

    def set_answers(self, answers, _format=None):
        self.remove_answers()
        self.current_answers = answers
        if _format == 'scale':
            size = (1, len(answers))
        else:
            size = (2, -(-len(answers) // 2))
        b_size = (size[0] + 2, size[1] + 2)
        topSpacer = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        bottomSpacer = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        leftSpacer = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        rightSpacer = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.ui.answersLayout.addItem(topSpacer, 0, 0, 1, b_size[1])
        self.ui.answersLayout.addItem(bottomSpacer, b_size[1], 0, 1, b_size[1])
        self.ui.answersLayout.addItem(leftSpacer, 1, 0, size[1], 1)
        self.ui.answersLayout.addItem(rightSpacer, 1, size[1] + 1, size[1], 1)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.ui.answerChecks = []
        for i in range(0, size[0]):
            for j in range(0, size[1]):
                a_index = i * size[1] + j
                if a_index < len(answers):
                    answer_check = QtWidgets.QCheckBox(self.ui.answersBox)
                    sizePolicy.setHeightForWidth(answer_check.sizePolicy().hasHeightForWidth())
                    answer_check.setSizePolicy(sizePolicy)
                    answer_check.setFont(font)
                    answer_check.setObjectName('answer_check_' + str(a_index))
                    answer_check.setText(
                        QtWidgets.QApplication.translate("EmotionQuestionnaire", answers[a_index], None, -1))
                    answer_check.clicked.connect(self.generate_answer_function(answer_check))
                    self.ui.answerChecks.append(answer_check)
                    self.ui.answersLayout.addWidget(answer_check, i + 1, j + 1, 1, 1)
                    self.answer_key[answers[a_index]] = answer_check

    def remove_answers(self):
        self.answer_key.clear()
        while not self.ui.answersLayout.isEmpty():
            item = self.ui.answersLayout.takeAt(0)
            if not item.isEmpty():
                widget = item.widget()
                widget.deleteLater()
                del widget
            self.ui.answersLayout.removeItem(item)

    def generate_answer_function(self, answer_check):
        return lambda v: self.answer_toggle(answer_check, v)

    def answer_toggle(self, answer_check, value):
        self.answer(answer_check, value)
        if self.multi_answers > 0:
            self.limit_answer(self.multi_answers, answer_check)

    def answer(self, check_widget, value):
        answer = self.answer_key.inverse[check_widget]
        self.selected_answer = answer
        event = {'_type': 'Questionnaire', 'SubType': 'AnswerSelected', 'File': self.path.name,
                 'Question': self.current_question, 'Answer': answer, 'Value': value}
        self.answer_action(event=event, caller=self)

    def limit_answer(self, limit, last):
        available = limit
        other_answers = self.answer_key.copy()
        other_answers.inverse.pop(last)
        for answer in other_answers.values():
            if answer.isChecked():
                if available > 1:
                    available -= 1
                else:
                    answer.setChecked(False)

    def default_answer(self, event=None, caller=None):
        pass

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.number_key.inverse:
            number = self.number_key.inverse[key]
            if number < len(self.current_answers):
                check_widget = self.answer_key[self.current_answers[number]]
                check_widget.setChecked(True)
                self.answer_toggle(check_widget, True)
        elif key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self._continue()
        elif key == QtCore.Qt.Key_Backspace:
            self.previous()
        event.accept()

    def _continue(self):
        self.q_index += 1
        event = {'_type': 'Questionnaire', 'Subtype': 'AnswerConfirmed', 'File': self.path.name,
                 'Question': self.current_question, 'Answer': self.selected_answer}
        if self.q_index < len(self.qa):
            self.next_action(event=event, caller=self)
        else:
            self.finish_action(event=event, caller=self)

    def default_next(self, event=None, caller=None):
        if self.q_index < len(self.qa) - 1:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Done", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Previous", None, -1))
        qa = self.qa[self.q_index]
        self.set_color(qa['color'])
        self.set_question(qa['question'])
        self.set_answers(qa['answers'], qa['format'])

    def default_finish(self, event=None, caller=None):
        print("Not Connected")

    def previous(self):
        if self.q_index > 0:
            self.q_index -= 1
            event = {'_type': 'Questionnaire', 'Subtype': 'AnswerRetracted', 'File': self.path.name,
                     'Question': self.qa[self.q_index]['question']}
            self.previous_action(event=event, caller=self)
        else:
            event = {'_type': 'Questionnaire', 'Subtype': 'Exited', 'File': self.path.name}
            self.back_action(event=event, caller=self)

    def default_previous(self, event=None, caller=None):
        if self.q_index > 0:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Exit", None, -1))
        qa = self.qa[self.q_index]
        self.set_color(qa['color'])
        self.set_question(qa['question'])
        self.set_answers(qa['answers'], qa['format'])

    def default_back(self, event=None, caller=None):
        print('There is no going back')


class FinishWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._path = None
        self.run_action = self.default_run

        self.ui = Ui_EmotionFinish()
        self.ui.setupUi(self)

        self.text = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def load_file(self, file):
        if file is not None:
            self.path = file
        pixmap = QtGui.QPixmap(self.path.as_posix())
        self.ui.imageSpace.setPixmap(pixmap)

    def start(self):
        event = {'_type': 'Finished'}
        self.run_action(event=event, caller=self)

    def default_run(self, event=None, caller=None):
        print('finish')


class VideoPlayerWidget(QWidget):
    def __init__(self, frame_action=None, finish_action=None, **kwargs):
        super(VideoPlayerWidget, self).__init__(**kwargs)
        if frame_action is None:
            self.frame_action = self.default_frame
        else:
            self.frame_action = frame_action
        if finish_action is None:
            self.finish_action = self.default_finish
        else:
            self.finish_action = finish_action

        self.ui = Ui_EmotionVideoPlayer()
        self.ui.setupUi(self)
        self.backgroundPalette = QtGui.QPalette()
        self.backgroundPalette.setColor(QtGui.QPalette.Background, QtGui.QColor(0, 0, 0))
        self.setAutoFillBackground(True)
        self.setPalette(self.backgroundPalette)

        self.ui.videoPlayer = QtMultimediaWidgets.QVideoWidget()
        self.ui.gridLayout.addWidget(self.ui.videoPlayer, 1, 1, 1, 1)

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
        event = {'_type': 'Video', 'SubType': 'Frame', 'Video': self.video.name, 'FrameNumber': self.frame_number}
        self.frame_action(frame, self.frame_number, event=event, caller=self)

    def default_frame(self, frame=None, number=None, event=None, caller=None):
        print(QtCore.QTime.currentTime().toString("hh:mm:ss.zzzz"))

    def status_check(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.finish()

    def finish(self):
        event = {'_type': 'Video', 'SubType': 'Finished', 'Video': self.video}
        self.finish_action(event=event, caller=self)

    def default_finish(self, event=None, caller=None):
        print("Done!")
