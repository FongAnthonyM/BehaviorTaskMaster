# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'emotionrating.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_EmotionQuestionnaire(object):
    def setupUi(self, EmotionQuestionnaire):
        if not EmotionQuestionnaire.objectName():
            EmotionQuestionnaire.setObjectName(u"EmotionQuestionnaire")
        EmotionQuestionnaire.resize(1024, 768)
        self.widgetLayout = QGridLayout(EmotionQuestionnaire)
        self.widgetLayout.setObjectName(u"widgetLayout")
        self.horizontalSpacerButtons = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.horizontalSpacerButtons, 9, 3, 1, 1)

        self.titleLabel = QLabel(EmotionQuestionnaire)
        self.titleLabel.setObjectName(u"titleLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(20)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.widgetLayout.addWidget(self.titleLabel, 2, 2, 1, 3)

        self.verticalSpacerTitle = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.widgetLayout.addItem(self.verticalSpacerTitle, 3, 2, 1, 3)

        self.horizontalSpacer_2 = QSpacerItem(60, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.horizontalSpacer_2, 10, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(60, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.horizontalSpacer, 10, 5, 1, 1)

        self.backButton = QPushButton(EmotionQuestionnaire)
        self.backButton.setObjectName(u"backButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.backButton.sizePolicy().hasHeightForWidth())
        self.backButton.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(16)
        self.backButton.setFont(font1)

        self.widgetLayout.addWidget(self.backButton, 9, 1, 1, 2)

        self.verticalSpacerTop = QSpacerItem(688, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.widgetLayout.addItem(self.verticalSpacerTop, 0, 2, 1, 3)

        self.continueButton = QPushButton(EmotionQuestionnaire)
        self.continueButton.setObjectName(u"continueButton")
        sizePolicy1.setHeightForWidth(self.continueButton.sizePolicy().hasHeightForWidth())
        self.continueButton.setSizePolicy(sizePolicy1)
        self.continueButton.setFont(font1)

        self.widgetLayout.addWidget(self.continueButton, 9, 4, 1, 2)

        self.verticalSpacerBottom = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.widgetLayout.addItem(self.verticalSpacerBottom, 10, 2, 1, 3)

        self.answersBox = QGroupBox(EmotionQuestionnaire)
        self.answersBox.setObjectName(u"answersBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.answersBox.sizePolicy().hasHeightForWidth())
        self.answersBox.setSizePolicy(sizePolicy2)
        self.answersBox.setMinimumSize(QSize(0, 150))
        font2 = QFont()
        font2.setPointSize(8)
        self.answersBox.setFont(font2)
        self.answersLayout = QGridLayout(self.answersBox)
        self.answersLayout.setObjectName(u"answersLayout")
        self.leftSpacer = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.answersLayout.addItem(self.leftSpacer, 1, 0, 2, 1)

        self.rightSpacer = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.answersLayout.addItem(self.rightSpacer, 1, 2, 2, 1)

        self.bottomSpacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.answersLayout.addItem(self.bottomSpacer, 4, 0, 1, 3)

        self.topSpacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.answersLayout.addItem(self.topSpacer, 0, 0, 1, 3)


        self.widgetLayout.addWidget(self.answersBox, 8, 1, 1, 5)

        self.horizontalSpacerRight = QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.horizontalSpacerRight, 4, 6, 7, 1)

        self.horizontalSpacerLeft = QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.horizontalSpacerLeft, 4, 0, 7, 1)

        self.colorSpacer = QPushButton(EmotionQuestionnaire)
        self.colorSpacer.setObjectName(u"colorSpacer")
        self.colorSpacer.setEnabled(False)
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.colorSpacer.sizePolicy().hasHeightForWidth())
        self.colorSpacer.setSizePolicy(sizePolicy3)

        self.widgetLayout.addWidget(self.colorSpacer, 0, 5, 4, 1)

        self.instructionsLabel = QLabel(EmotionQuestionnaire)
        self.instructionsLabel.setObjectName(u"instructionsLabel")
        sizePolicy.setHeightForWidth(self.instructionsLabel.sizePolicy().hasHeightForWidth())
        self.instructionsLabel.setSizePolicy(sizePolicy)
        self.instructionsLabel.setFont(font1)
        self.instructionsLabel.setAlignment(Qt.AlignCenter)

        self.widgetLayout.addWidget(self.instructionsLabel, 4, 2, 1, 3)

        self.rightTitleSpacer = QSpacerItem(100, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.rightTitleSpacer, 4, 5, 1, 1)

        self.leftTitleSpacer = QSpacerItem(100, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.widgetLayout.addItem(self.leftTitleSpacer, 4, 1, 1, 1)


        self.retranslateUi(EmotionQuestionnaire)

        QMetaObject.connectSlotsByName(EmotionQuestionnaire)
    # setupUi

    def retranslateUi(self, EmotionQuestionnaire):
        EmotionQuestionnaire.setWindowTitle(QCoreApplication.translate("EmotionQuestionnaire", u"EmotionTaskQuestionnaire", None))
        self.titleLabel.setText(QCoreApplication.translate("EmotionQuestionnaire", u"Emotion Rating", None))
        self.backButton.setText("")
        self.continueButton.setText(QCoreApplication.translate("EmotionQuestionnaire", u"Next", None))
        self.answersBox.setTitle("")
        self.colorSpacer.setText("")
        self.instructionsLabel.setText(QCoreApplication.translate("EmotionQuestionnaire", u"Please rate how you felt while watching the video:", None))
    # retranslateUi

