#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" taskwidgets.py
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

# Downloaded Libraries #
from bidict import bidict
from bidict import frozenbidict
import toml
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction

# Local Libraries #
from QtUtility.utilitywidgets import WidgetStack
from QtUtility.UI.emotioninstructions import Ui_EmotionInstructions
from QtUtility.UI.emotionwashout import Ui_EmotionWashout
from QtUtility.UI.emotionquestionnaire import Ui_EmotionQuestionnaire
from QtUtility.UI.emotionvideoplayer import Ui_EmotionVideoPlayer
from QtUtility.UI.emotionfinish import Ui_EmotionFinish


# Definitions #
# Classes #
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
