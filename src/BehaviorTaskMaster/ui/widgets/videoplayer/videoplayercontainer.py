""" videoplayercontainer.py
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
from PySide2.QtCore import QUrl

# Local Packages #
from ..base import BaseWidgetContainer
from .videoplayerwidget import VideoPlayerWidget


# Definitions #
# Classes #
class VideoPlayerContainer(BaseWidgetContainer):
    def __init__(self, name="VideoPlayer", source="path", path=None, url=None, events=None, init=False):
        BaseWidgetContainer.__init__(self, name, init)
        self._frame_action = self.frame_process
        self._finish_action = None

        self.events = events

        self._media_player = None
        self.source = source

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('emotionTask', 'default.mp4')
        else:
            self.path = path

        self._url = None
        if url is None:
            self._url = QUrl("http://clips.vorwaerts-gmbh.de/VfE_html5.mp4")
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
        if isinstance(value, QUrl) or value is None:
            self._url = value
        else:
            self._url = QUrl(value)

    @property
    def video(self):
        if self.source == "url":
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
        event = {'SubType': 'VideoStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)
        self.widget.play()

    def load_video(self, video=None):
        if video is None:
            self.widget.set_video(self.video)
        else:
            self.widget.set_video(video)

    def frame_process(self, frame=None, number=None, event=None, caller=None):
        # could use frame metadata if is exists: print(frame.metaData(str_name))
        self.events.append(**event)
        # print(self.events[-1])
