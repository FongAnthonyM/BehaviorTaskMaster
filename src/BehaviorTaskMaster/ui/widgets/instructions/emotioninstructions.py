# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotioninstructions.ui',
# licensing of 'emotioninstructions.ui' applies.
#
# Created: Fri Sep 27 09:45:30 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionInstructions(object):
    def setupUi(self, EmotionInstructions):
        EmotionInstructions.setObjectName("InstructionsContainer")
        EmotionInstructions.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionInstructions)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(688, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 7, 1, 1, 3)
        self.okButton = QtWidgets.QPushButton(EmotionInstructions)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.okButton.setFont(font)
        self.okButton.setObjectName("okButton")
        self.gridLayout.addWidget(self.okButton, 5, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 4, 8, 1)
        self.backButton = QtWidgets.QPushButton(EmotionInstructions)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.backButton.setFont(font)
        self.backButton.setObjectName("backButton")
        self.gridLayout.addWidget(self.backButton, 5, 3, 1, 1)
        self.titleLabel = QtWidgets.QLabel(EmotionInstructions)
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
        self.gridLayout.addWidget(self.titleLabel, 1, 1, 1, 3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem4, 2, 1, 1, 3)
        self.textBrowser = QtWidgets.QTextBrowser(EmotionInstructions)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 3, 1, 1, 3)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 0, 0, 8, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem6, 4, 1, 1, 3)

        self.retranslateUi(EmotionInstructions)
        QtCore.QMetaObject.connectSlotsByName(EmotionInstructions)

    def retranslateUi(self, EmotionInstructions):
        EmotionInstructions.setWindowTitle(QtWidgets.QApplication.translate("InstructionsContainer", "InstructionsContainer", None, -1))
        self.okButton.setText(QtWidgets.QApplication.translate("InstructionsContainer", "OK", None, -1))
        self.backButton.setText(QtWidgets.QApplication.translate("InstructionsContainer", "Back", None, -1))
        self.titleLabel.setText(QtWidgets.QApplication.translate("InstructionsContainer", "Instructions", None, -1))

