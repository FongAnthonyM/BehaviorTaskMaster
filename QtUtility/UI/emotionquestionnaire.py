# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionquestionnaire.ui',
# licensing of 'emotionquestionnaire.ui' applies.
#
# Created: Fri Oct 11 11:35:30 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionQuestionnaire(object):
    def setupUi(self, EmotionQuestionnaire):
        EmotionQuestionnaire.setObjectName("EmotionQuestionnaire")
        EmotionQuestionnaire.resize(800, 600)
        self.widgetLayout = QtWidgets.QGridLayout(EmotionQuestionnaire)
        self.widgetLayout.setObjectName("widgetLayout")
        spacerItem = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.widgetLayout.addItem(spacerItem, 5, 6, 6, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.widgetLayout.addItem(spacerItem1, 9, 3, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.widgetLayout.addItem(spacerItem2, 10, 2, 1, 3)
        spacerItem3 = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.widgetLayout.addItem(spacerItem3, 5, 0, 6, 1)
        spacerItem4 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.widgetLayout.addItem(spacerItem4, 10, 5, 1, 1)
        self.titleLabel = QtWidgets.QLabel(EmotionQuestionnaire)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.widgetLayout.addWidget(self.titleLabel, 2, 2, 1, 3)
        self.continueButton = QtWidgets.QPushButton(EmotionQuestionnaire)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.continueButton.sizePolicy().hasHeightForWidth())
        self.continueButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.continueButton.setFont(font)
        self.continueButton.setObjectName("continueButton")
        self.widgetLayout.addWidget(self.continueButton, 9, 4, 1, 2)
        spacerItem5 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.widgetLayout.addItem(spacerItem5, 3, 2, 1, 3)
        spacerItem6 = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.widgetLayout.addItem(spacerItem6, 10, 1, 1, 1)
        self.backButton = QtWidgets.QPushButton(EmotionQuestionnaire)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.backButton.setFont(font)
        self.backButton.setText("")
        self.backButton.setObjectName("backButton")
        self.widgetLayout.addWidget(self.backButton, 9, 1, 1, 2)
        self.QuestionBox = QtWidgets.QGroupBox(EmotionQuestionnaire)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QuestionBox.sizePolicy().hasHeightForWidth())
        self.QuestionBox.setSizePolicy(sizePolicy)
        self.QuestionBox.setTitle("")
        self.QuestionBox.setObjectName("QuestionBox")
        self.questionLayout = QtWidgets.QGridLayout(self.QuestionBox)
        self.questionLayout.setObjectName("questionLayout")
        self.questionBrowser = QtWidgets.QTextBrowser(self.QuestionBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.questionBrowser.sizePolicy().hasHeightForWidth())
        self.questionBrowser.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.questionBrowser.setFont(font)
        self.questionBrowser.setObjectName("questionBrowser")
        self.questionLayout.addWidget(self.questionBrowser, 0, 0, 1, 1)
        self.widgetLayout.addWidget(self.QuestionBox, 5, 1, 1, 5)
        self.answersBox = QtWidgets.QGroupBox(EmotionQuestionnaire)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.answersBox.sizePolicy().hasHeightForWidth())
        self.answersBox.setSizePolicy(sizePolicy)
        self.answersBox.setMinimumSize(QtCore.QSize(0, 150))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.answersBox.setFont(font)
        self.answersBox.setTitle("")
        self.answersBox.setObjectName("answersBox")
        self.answersLayout = QtWidgets.QGridLayout(self.answersBox)
        self.answersLayout.setObjectName("answersLayout")
        spacerItem7 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.answersLayout.addItem(spacerItem7, 1, 0, 2, 1)
        spacerItem8 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.answersLayout.addItem(spacerItem8, 1, 2, 2, 1)
        spacerItem9 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.answersLayout.addItem(spacerItem9, 4, 0, 1, 3)
        spacerItem10 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.answersLayout.addItem(spacerItem10, 0, 0, 1, 3)
        self.widgetLayout.addWidget(self.answersBox, 8, 1, 1, 5)
        spacerItem11 = QtWidgets.QSpacerItem(688, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.widgetLayout.addItem(spacerItem11, 0, 2, 1, 3)
        self.colorSpacer = QtWidgets.QPushButton(EmotionQuestionnaire)
        self.colorSpacer.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorSpacer.sizePolicy().hasHeightForWidth())
        self.colorSpacer.setSizePolicy(sizePolicy)
        self.colorSpacer.setText("")
        self.colorSpacer.setObjectName("colorSpacer")
        self.widgetLayout.addWidget(self.colorSpacer, 0, 5, 4, 2)

        self.retranslateUi(EmotionQuestionnaire)
        QtCore.QMetaObject.connectSlotsByName(EmotionQuestionnaire)

    def retranslateUi(self, EmotionQuestionnaire):
        EmotionQuestionnaire.setWindowTitle(QtWidgets.QApplication.translate("EmotionQuestionnaire", "EmotionTaskQuestionnaire", None, -1))
        self.titleLabel.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Questionnaire", None, -1))
        self.continueButton.setText(QtWidgets.QApplication.translate("EmotionQuestionnaire", "Next", None, -1))

