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
from bidict import bidict
from bidict import frozenbidict
import toml
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction

# Local Packages #
from .questionnaire import Ui_Questionnaire


# Definitions #
# Classes #
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

        self.ui = Ui_Questionnaire()
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
        self.selected_answer = ""

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
                        QtWidgets.QApplication.translate("QuestionnaireContainer", answers[a_index], None, -1))
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
        if answer is None:
            answer = ""
        self.selected_answer = answer
        event = {'type_': 'Questionnaire_AnswerSelected', 'File': self.path.name,
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
        event = {'type_': 'Questionnaire_AnswerConfirmed', 'File': self.path.name,
                 'Question': self.current_question, 'Answer': self.selected_answer}
        if self.q_index < len(self.qa):
            self.next_action(event=event, caller=self)
        else:
            self.finish_action(event=event, caller=self)

    def default_next(self, event=None, caller=None):
        if self.q_index < len(self.qa) - 1:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Done", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Previous", None, -1))
        qa = self.qa[self.q_index]
        self.set_color(qa['color'])
        self.set_question(qa['question'])
        self.set_answers(qa['answers'], qa['format'])

    def default_finish(self, event=None, caller=None):
        print("Not Connected")

    def previous(self):
        if self.q_index > 0:
            self.q_index -= 1
            event = {'type_': 'Questionnaire_AnswerRetracted', 'File': self.path.name,
                     'Question': self.qa[self.q_index]['question']}
            self.previous_action(event=event, caller=self)
        else:
            event = {'type_': 'Questionnaire_Exited', 'File': self.path.name}
            self.back_action(event=event, caller=self)

    def default_previous(self, event=None, caller=None):
        if self.q_index > 0:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("QuestionnaireContainer", "Exit", None, -1))
        qa = self.qa[self.q_index]
        self.set_color(qa['color'])
        self.set_question(qa['question'])
        self.set_answers(qa['answers'], qa['format'])

    def default_back(self, event=None, caller=None):
        print('There is no going back')
