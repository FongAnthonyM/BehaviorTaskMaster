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

        self.sequencer = WidgetContainerSequencer()
        self.task_window.sequencer = self.sequencer

        self.parameters = EmotionParameters()
        self.control = EmotionControl()
        self.instructions = EmotionInstructions()
        self.washout = EmotionWashout()
        self.video_player = EmotionVideoPlayer()
        self.questionnaire = None
        self.finished = None

        self.control.task_window = self.task_window
        self.control.player = EmotionVideoPlayer

        self.task_start_time = None

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

    def start_task(self):
        self.generate_sequence()
        self.task_window.show()
        self.sequencer.start()

    def generate_sequence(self):
        self.sequencer.clear()
        self.sequencer.insert(self.instructions, ok_action=self.advance, back_action=self.setup_task)
        for i in range(0, self.parameters.n_videos):
            self.sequencer.insert(self.washout, milliseconds=2000, timer_action=self.advance)
            self.sequencer.insert(self.video_player, source="url",)

    def advance(self):
        next(self.sequencer)

    def test(self):
        print('Success')


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
            self.construct()

    @abstractmethod
    def construct(self):
        self.widget = None

    def destroy(self):
        self.widget = None

    @abstractmethod
    def add_to_stack(self, stack=None, name=None):
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

    @property
    def blocks(self):
        return self.widget.blocks

    @property
    def loops(self):
        return self.widget.loops

    @property
    def randomize(self):
        return self.widget.randomize

    def construct(self):
        self.widget = ParametersWidget()

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.widget = ParametersWidget()
        super().add_to_stack(stack, name)

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
        videos.setEditable(False)
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
    def __init__(self, name="EmotionControl", init=False):
        WidgetContainer.__init__(self, name, init)
        self.back_action = self.remove_from_stack

    @property
    def task_window(self):
        return self.widget.task_window

    @task_window.setter
    def task_window(self, value):
        self.widget.task_window = value

    @property
    def player(self):
        return self.widget.player

    @player.setter
    def player(self, value):
        self.widget.player = value

    @property
    def blocks(self):
        return self.widget.blocks

    @blocks.setter
    def blocks(self, value):
        self.widget.blocks = value

    def construct(self):
        self.widget = ControlWidget()

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.widget = ControlWidget()
        super().add_to_stack(stack, name)

    def run(self, back_action=None):
        if back_action is not None:
            self.back_action = back_action

        self.widget.back_action = self.back_action
        super().run()


class ControlWidget(QWidget):
    def __init__(self, player=None, init=False, **kwargs):
        super().__init__(**kwargs)
        self.back_action = self.default_back

        self.ui = Ui_EmotionControl()
        self.ui.setupUi(self)

        self.play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
        self.stop_icon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.skip_icon = self.style().standardIcon(QStyle.SP_MediaSkipForward)
        self.volume_icon = self.style().standardIcon(QStyle.SP_MediaVolume)
        self.mute_icon = self.style().standardIcon(QStyle.SP_MediaVolumeMuted)

        self.task_window = None
        self._player = player
        self.media_player = player.player

        self.blocks = None
        if init:
            self.construct()

    def construct(self):
        self._construct_backAction()
        self._construct_fullScreenAction()
        self._construct_player_buttons()
        self._construct_volume_controls()
        self.update_buttons(self.media_player.state())

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        self._player = value
        self.media_player = value.player

    def _construct_backAction(self):
        self.ui.backButton.clicked.connect(self.back)

    def _construct_fullScreenAction(self):
        self.ui.fullscreenButton.clicked.connect(self.task_window.fullscreen_action)

    def _constrcut_showAction(self):
        self.ui.showButton.clicked.connect(self.task_window.show)

    def _construct_player_controls(self):
        self.media_player.stateChanged.connect(self.updateButtons)
        self.ui.playButton.setIcon(self.play_icon)
        self.ui.stopButton.setIcon(self.stop_icon)
        self.ui.stopButton.clicked.connect(self.player.stop)
        self.ui.skipButton.setIcon(self.skip_icon)
        self.ui.skipButton.clicked.connect(self.skip_action)

    def _construct_volume_controls(self):
        self.media_player.stateChanged.connect(self.update_buttons)
        self.ui.muteButton.setIcon(self.volume_icon)

        self.ui.volumeSlider.setValue(self.media_player.volume())
        self.ui.volumeSlider.valueChanged.connect(self.media_player.setVolume)








    def update_buttons(self, state):
        self.ui.stopButton.setEnabled(state != QtMultimedia.QMediaPlayer.StoppedState)
        if state == QtMultimedia.QMediaPlayer.PlayingState:
            self.ui.playButton.clicked.connect(self.media_player.pause)
            self.ui.playButton.setIcon(self.pause_icon)
        elif state != QtMultimedia.QMediaPlayer.PlayingState:
            self.ui.playButton.clicked.connect(self.player.play)
            self.ui.playButton.setIcon(self.play_icon)

    def back(self):
        self.back_action()

    def default_back(self):
        sys.exit()

class EmotionInstructions(WidgetContainer):
    def __init__(self, name="Instructions", path=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack

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

    def construct(self):
        self.widget = InstructionsWidget()

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.widget = InstructionsWidget()
        super().add_to_stack(stack, name)

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
        self.ok_action()

    def default_ok(self):
        print("Not Connected")

    def back(self):
        self.back_action()

    def default_back(self):
        sys.exit()


class EmotionWashout(WidgetContainer):
    def __init__(self, name="Washout", init=False):
        WidgetContainer.__init__(self, name, init)
        self.timer_action = None

        self.milliseconds = 0
        self.font_size = 100
        self.text = "X"

    def construct(self):
        self.widget = WashoutWidget()

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.widget = WashoutWidget()
        super().add_to_stack(stack, name)

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
        self.timer_action()

    def default_timer_action(self):
        print("Time is up!")


class EmotionVideoPlayer(WidgetContainer):
    def __init__(self, name="VideoPlayer", source="path", path=None, url=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.finish_action = None

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
        return self.widget.mediaPlayer

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

    def construct(self):
        self.widget = VideoPlayerWidget()

    def add_to_stack(self, stack=None, name=None):
        if self.widget is None:
            self.widget = VideoPlayerWidget()
        super().add_to_stack(stack, name)

    def run(self, source="path", path=None, url=None, finish_action=None):
        if source is not None:
            self.source = source
        if path is not None:
            self.path = path
        if url is not None:
            self.url = url
        if finish_action is not None:
            self.finish_action = finish_action

        self.widget.finish_action = self.finish_action
        self.load_video()
        super().run()
        self.widget.frameProbe.videoFrameProbed.connect(self.widget.frame)
        self.widget.frameProbe.setSource(self.widget.mediaPlayer)
        print(self.widget.frameProbe.isActive())
        self.widget.play()

    def load_video(self):
        self.widget.set_video(self.video)


class VideoPlayerWidget(QWidget):
    def __init__(self):
        super(VideoPlayerWidget, self).__init__()
        self.frame_action = self.default_frame
        self.finish_action = self.default_finish

        self.ui = Ui_EmotionVideoPlayer()
        self.ui.setupUi(self)

        self.ui.videoPlayer = QtMultimediaWidgets.QVideoWidget()
        self.ui.gridLayout.addWidget(self.ui.videoPlayer, 0, 0, 1, 1)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(self, QtMultimedia.QMediaPlayer.VideoSurface)
        self.video_item = QtMultimediaWidgets.QGraphicsVideoItem()
        self.mediaPlayer.setVideoOutput(self.ui.videoPlayer)

        self.frameProbe = QtMultimedia.QVideoProbe(self)
        self.frameProbe.setSource(self.mediaPlayer)

        print(self.frameProbe.isActive())

    def set_video(self, video):
        if isinstance(video, pathlib.Path) or isinstance(video, str):
            video = QtCore.QUrl.fromLocalFile(video)
        if isinstance(video, QtCore.QUrl):
            video = QtMultimedia.QMediaContent(video)
        self.mediaPlayer.setMedia(video)

    def play(self):
        self.mediaPlayer.play()

    @Slot()
    def frame(self):
        self.frame_action()

    def default_frame(self):
        print(QtCore.QTime.currentTime().toString("hh:mm:ss.zzzz"))
        print("Frame")

    def finish(self):
        self.finish_action()

    def default_finish(self):
        print("Done!")
