# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionwashout.ui',
# licensing of 'emotionwashout.ui' applies.
#
# Created: Fri Oct 11 11:20:23 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionWashout(object):
    def setupUi(self, EmotionWashout):
        EmotionWashout.setObjectName("EmotionWashout")
        EmotionWashout.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionWashout)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(150, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(EmotionWashout)
        font = QtGui.QFont()
        font.setPointSize(100)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 150, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 150, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 2, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(150, 150, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)
        self.colorSpacer = QtWidgets.QPushButton(EmotionWashout)
        self.colorSpacer.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorSpacer.sizePolicy().hasHeightForWidth())
        self.colorSpacer.setSizePolicy(sizePolicy)
        self.colorSpacer.setMaximumSize(QtCore.QSize(150, 150))
        self.colorSpacer.setText("")
        self.colorSpacer.setObjectName("colorSpacer")
        self.gridLayout.addWidget(self.colorSpacer, 0, 3, 1, 1)

        self.retranslateUi(EmotionWashout)
        QtCore.QMetaObject.connectSlotsByName(EmotionWashout)

    def retranslateUi(self, EmotionWashout):
        EmotionWashout.setWindowTitle(QtWidgets.QApplication.translate("EmotionWashout", "EmotionWashout", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("EmotionWashout", "X", None, -1))

