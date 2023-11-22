""" ratingwidget.py

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

# Third-Party Packages #
from bidict import bidict
from bidict import frozenbidict
import toml
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction

# Local Packages #
from .emotionrating import Ui_EmotionRating


# Definitions #
# Classes #
class RatingWidget(QWidget):
    number_key = frozenbidict({
        0: QtCore.Qt.Key_0,
        1: QtCore.Qt.Key_1,
        2: QtCore.Qt.Key_2,
        3: QtCore.Qt.Key_3,
        4: QtCore.Qt.Key_4,
        5: QtCore.Qt.Key_5,
        6: QtCore.Qt.Key_6,
        7: QtCore.Qt.Key_7,
        8: QtCore.Qt.Key_8,
        9: QtCore.Qt.Key_9,
    })

    def __init__(
        self,
        next_action=None,
        finish_action=None,
        previous_action=None,
        back_action=None,
        answer_action=None,
        **kwargs,
    ) -> None:
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

        self.ui = Ui_EmotionRating()
        self.ui.setupUi(self)

        self.ui.continueButton.clicked.connect(self._continue)
        self.ui.backButton.clicked.connect(self.previous)

        self.continueAction = QAction("Continue", self)
        self.continueAction.setShortcut(QKeySequence("Shift+Return"))
        self.continueAction.triggered.connect(self._continue)
        self.addAction(self.continueAction)

        self._path = None
        self.text = None
        self.ratings = []
        self.answers = []
        self.rating_key = {}
        self.rating_items = {}
        self.rating_index = 0

        self.current_answers = None
        self.current_color = None
        self.selected_ratings = {}

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
            r_file = toml.load(self.path)
            self.ratings = r_file["Ratings"]
            self.r_index = 0
            ratings = self.ratings[self.r_index]
            self.set_color(ratings["color"])
            self.set_ratings(ratings["items"], ratings["ratings"])

    def set_color(self, color):
        if color is not None:
            self.ui.colorSpacer.setStyleSheet('background-color:rgb(' + color + ')')
            self.current_color = color

    def set_ratings(self, items, ratings):
        self.remove_answers()
        self.current_answers = items

        size = (len(items) + 1, len(ratings) + 1)
        b_size = (size[0] + 2, size[1] + 2)

        topSpacer = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        bottomSpacer = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        leftSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        rightSpacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.ui.answersLayout.addItem(topSpacer, 0, 0, 1, b_size[1])
        self.ui.answersLayout.addItem(bottomSpacer, b_size[1], 0, 1, b_size[1])
        self.ui.answersLayout.addItem(leftSpacer, 1, 0, size[0], 1)
        self.ui.answersLayout.addItem(rightSpacer, 1, b_size[1] - 1, size[0], 1)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.ui.answerChecks = []
        self.ui.answersLayout.setAlignment(QtGui.Qt.AlignCenter)

        for j, rating in enumerate(ratings):
            item_label = QtWidgets.QLabel(self.ui.answersBox)
            item_label.setFont(font)
            item_label.setAlignment(QtGui.Qt.AlignCenter)
            item_label.setObjectName(f"{rating}Label")
            item_label.setText(QtWidgets.QApplication.translate("RatingContainer", rating, None, -1))
            #item_label.setStyleSheet("margin-left:50%; margin-right:50%;")
            self.ui.answersLayout.addWidget(item_label, 1, j + 2, 1, 1)

        for i, item in enumerate(items):
            self.rating_items[item] = set()
            self.selected_ratings[item] = -1
            item_label = QtWidgets.QLabel(self.ui.answersBox)
            item_label.setObjectName(f"{item}Label")
            item_label.setFont(font)
            item_label.setText(QtWidgets.QApplication.translate("RatingContainer", item, None, -1))
            #item_label.setStyleSheet("margin-left:50%; margin-right:50%;")
            self.ui.answersLayout.addWidget(item_label, i + 2, 1, 1, 1)
            for j, rating in enumerate(ratings):
                answer_radio = QtWidgets.QRadioButton(self.ui.answersBox)
                answer_radio.setStyleSheet("QRadioButton::indicator { width: 40px; height: 40px;} QRadioButton{margin-left:50%; margin-right:50%;};")
                #sizePolicy.setHeightForWidth(answer_radio.sizePolicy().hasHeightForWidth())
                #answer_radio.setSizePolicy(sizePolicy)
                answer_radio.setObjectName(f"answer_check_{item}_{j}")
                answer_radio.clicked.connect(self.generate_answer_function(answer_radio))
                answer_radio.setAutoExclusive(False)
                self.ui.answerChecks.append(answer_radio)
                self.ui.answersLayout.addWidget(answer_radio, i + 2, j + 2, 1, 1)
                self.rating_key[answer_radio] = {"item": item, "rating": str(j)}
                self.rating_items[item].add(answer_radio)

    def remove_answers(self):
        self.rating_key.clear()
        self.rating_items.clear()
        while not self.ui.answersLayout.isEmpty():
            item = self.ui.answersLayout.takeAt(0)
            if not item.isEmpty():
                widget = item.widget()
                widget.deleteLater()
                del widget
            self.ui.answersLayout.removeItem(item)

    def generate_answer_function(self, answer_radio):
        return lambda v: self.answer_toggle(answer_radio, v)

    def answer_toggle(self, answer_radio, value):
        answer = self.rating_key[answer_radio]
        item = answer["item"]
        rating = answer["rating"]

        self.answer(item, rating, value)
        self.limit_answer(item, answer_radio)

    def answer(self, item, rating, value):
        self.selected_ratings[item] = rating
        event = {'type_': 'Rating_AnswerSelected', 'File': self.path.name,
                 'Item': item, 'Rating': rating, 'Value': value}
        self.answer_action(event=event, caller=self)

    def limit_answer(self, item, answer_widget):
        other_answers = self.rating_items[item] - {answer_widget}
        for answer in other_answers:
            if answer.isChecked():
                answer.setChecked(False)

    def default_answer(self, event=None, caller=None):
        pass

    # def keyPressEvent(self, event):
    #     pass

    def _continue(self):
        self.r_index += 1
        event = {'type_': 'Rating_AnswerConfirmed', 'File': self.path.name}
        event.update(self.selected_ratings)
        if self.r_index < len(self.ratings):
            self.next_action(event=event, caller=self)
        else:
            self.finish_action(event=event, caller=self)

    def default_next(self, event=None, caller=None):
        if self.r_index < len(self.ratings) - 1:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Done", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Previous", None, -1))
        ratings = self.ratings[self.r_index]
        self.set_color(ratings["color"])
        self.set_ratings(ratings["items"], ratings["ratings"])

    def default_finish(self, event=None, caller=None):
        print("Not Connected")

    def previous(self):
        if self.r_index > 0:
            self.r_index -= 1
            event = {'type_': 'Rating_AnswerRetracted', 'File': self.path.name,
                     'Ratings': str(self.ratings[self.r_index]['ratings'])}
            self.previous_action(event=event, caller=self)
        else:
            event = {'type_': 'Rating_Exited', 'File': self.path.name}
            self.back_action(event=event, caller=self)

    def default_previous(self, event=None, caller=None):
        if self.r_index > 0:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Previous", None, -1))
        else:
            self.ui.continueButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Next", None, -1))
            self.ui.backButton.setText(QtWidgets.QApplication.translate("RatingContainer", "Exit", None, -1))
        ratings = self.ratings[self.r_index]
        self.set_color(ratings["color"])
        self.set_ratings(ratings["items"], ratings["ratings"])

    def default_back(self, event=None, caller=None):
        print('There is no going back')


if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication

    r_path = pathlib.Path.cwd().joinpath("rating.toml")

    app = QApplication(sys.argv)

    window = RatingWidget()
    window.load_file(r_path)
    window.show()

    sys.exit(app.exec_())
