""" taskwindow.py
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
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtWidgets import QWidget, QAction

# Local Packages #
from .emotionvideoplayer import Ui_EmotionVideoPlayer


# Definitions #
# Classes #
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
        # self.frameProbe.videoFrameProbed.connect(self.frame)
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
        event = {'type_': 'Video_Frame', 'Video': self.video.name, 'FrameNumber': self.frame_number}
        self.frame_action(frame, self.frame_number, event=event, caller=self)

    def default_frame(self, frame=None, number=None, event=None, caller=None):
        print(QtCore.QTime.currentTime().toString("hh:mm:ss.zzzz"))

    def status_check(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.finish()

    def finish(self):
        self.mediaPlayer.stop()
        self.mediaPlayer.setMedia(self.mediaPlayer.media())
        event = {'type_': 'Video_Finished', 'Video': self.video.as_posix()}
        self.finish_action(event=event, caller=self)

    def default_finish(self, event=None, caller=None):
        print("Done!")
