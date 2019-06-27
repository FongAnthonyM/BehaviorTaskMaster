# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionwashout.ui',
# licensing of 'emotionwashout.ui' applies.
#
# Created: Wed Jun 26 09:27:54 2019
#      by: pyside2-uic  running on PySide2 5.12.4
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionWashout(object):
    def setupUi(self, EmotionWashout):
        EmotionWashout.setObjectName("EmotionWashout")
        EmotionWashout.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionWashout)
        self.gridLayout.setObjectName("gridLayout")
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
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(EmotionWashout)
        QtCore.QMetaObject.connectSlotsByName(EmotionWashout)

    def retranslateUi(self, EmotionWashout):
        EmotionWashout.setWindowTitle(QtWidgets.QApplication.translate("EmotionWashout", "EmotionWashout", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("EmotionWashout", "X", None, -1))

