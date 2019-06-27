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
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction

# Local Libraries #
from .UI.emotionparameters import Ui_EmotionParameters
from .UI.emotioninstructions import Ui_EmotionInstructions
from .UI.emotionwashout import Ui_EmotionWashout
from .UI.emotionvideoplayer import Ui_EmotionVideoPlayer

########## Definitions ##########

# Classes #
class EmotionTask:
    def __init__(self, parent=None, stack=None, r_widget=None):
        self.parent = parent
        self.widget_stack = stack
        self.return_widget = r_widget

        self.sequencer = WidgetContainerSequencer()

        self.parameters = EmotionParameters()
        self.instructions = EmotionInstructions()
        self.washout = EmotionWashout()
        self.video_player = EmotionVideoPlayer()
        self.questionnaire = None
        self.finished = None




        self.task_start_time = None

    def load_task(self, stack=None):
        if stack is not None:
            self.widget_stack = stack

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.parameters.load(self.widget_stack)
        self.instructions.load(self.widget_stack)
        self.washout.load(self.widget_stack)
        self.video_player.load(self.widget_stack)

    def unload_task(self, back=True, clear_data=False):
        if back:
            self.widget_stack.set(self.return_widget)

        self.parameters.unload(False, clear_data)
        self.instructions.unload(False, clear_data)
        self.washout.unload(False, clear_data)
        self.video_player.unload(False, clear_data)

    def setup_task(self):
        self.parameters.run(self.start_task, self.unload_task)

    def start_task(self):
        self.generate_sequence()
        self.sequencer.start()

    def generate_sequence(self):
        self.sequencer.clear()
        self.sequencer.insert(self.instructions, ok_action=self.advance, back_action=self.setup_task)
        for i in range(0,self.parameters.n_videos):
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
            self.sequence.append({"widget":widget,"kwargs":kwargs})
            return len(self.sequence)
        else:
            self.sequence.insert(index, {"widget":widget,"kwargs":kwargs})
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
    def load(self, stack=None):
        if stack is not None:
            self.widget_stack = stack

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.widget_stack.add(self.widget, self.name)

    def unload(self, back=True, clear_data=False):
        if back:
            self.widget_stack.set(self.return_widget)

        self.widget_stack.remove(self.name)

        if clear_data:
            self.widget = None

    def make_active(self):
        self.widget_stack.set(self.name)

    def run(self):
        self.widget_stack.set(self.name)


class EmotionParameters(WidgetContainer):
    def __init__(self, name="EmotionParameters", init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.unload

        self.instruction_paths = []
        self.video_paths = []
        self.n_videos = 1
        self.loops = 1
        self.washout = 1000

    def construct(self):
        self.widget = ParametersWidget()

    def load(self, stack=None):
        if self.widget is None:
            self.widget = ParametersWidget()
        super().load(stack)

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        super().run()


class ParametersWidget(QWidget):
    def __init__(self):
        super(ParametersWidget, self).__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self.ui = Ui_EmotionParameters()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.ok)
        self.ui.backButton.clicked.connect(self.back)

        self.okAction = QAction("OK", self)
        self.okAction.setShortcut(QKeySequence("Shift+Return"))
        self.okAction.triggered.connect(self.ok_action)
        self.addAction(self.okAction)

    def ok(self):
        self.ok_action()

    def default_ok(self):
        print("Not Connected")

    def back(self):
        self.back_action()

    def default_back(self):
        sys.exit()


class EmotionInstructions(WidgetContainer):
    def __init__(self, name="Instructions", path=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.unload

        self._path = None
        if path is None:
            self._path = pathlib.Path.cwd().joinpath('emotionTask','instructions.txt')
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

    def load(self, stack=None):
        if self.widget is None:
            self.widget = InstructionsWidget()
        super().load(stack)

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

    def load(self, stack=None):
        if self.widget is None:
            self.widget = WashoutWidget()
        super().load(stack)

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

    def load(self, stack=None):
        if self.widget is None:
            self.widget = VideoPlayerWidget()
        super().load(stack)

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
        self.widget.play()

    def load_video(self):
        self.widget.set_video(self.video)


class VideoPlayerWidget(QWidget):
    def __init__(self):
        super(VideoPlayerWidget, self).__init__()
        self.finish_action = self.default_finish

        self.ui = Ui_EmotionVideoPlayer()
        self.ui.setupUi(self)

        self.ui.videoPlayer = QtMultimediaWidgets.QVideoWidget()
        self.ui.gridLayout.addWidget(self.ui.videoPlayer, 0, 0, 1, 1)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.ui.videoPlayer)

    def set_video(self, video):
        if isinstance(video, pathlib.Path) or isinstance(video, str):
            video = QtCore.QUrl.fromLocalFile(video)
        if isinstance(video, QtCore.QUrl):
            video = QtMultimedia.QMediaContent(video)
        self.mediaPlayer.setMedia(video)

    def play(self):
        self.mediaPlayer.play()

    def finish(self):
        self.finish_action()

    def default_finish(self):
        print("Done!")