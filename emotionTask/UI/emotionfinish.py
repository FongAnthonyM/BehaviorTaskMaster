# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionfinish.ui',
# licensing of 'emotionfinish.ui' applies.
#
# Created: Tue Oct  1 13:57:05 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionFinish(object):
    def setupUi(self, EmotionFinish):
        EmotionFinish.setObjectName("EmotionFinish")
        EmotionFinish.resize(836, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionFinish)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 2)
        self.titleLabel = QtWidgets.QLabel(EmotionFinish)
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
        self.gridLayout.addWidget(self.titleLabel, 1, 1, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(688, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 3, 5, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 0, 5, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem4, 4, 1, 1, 2)
        self.imageSpace = QtWidgets.QLabel(EmotionFinish)
        self.imageSpace.setText("")
        self.imageSpace.setAlignment(QtCore.Qt.AlignCenter)
        self.imageSpace.setObjectName("imageSpace")
        self.gridLayout.addWidget(self.imageSpace, 3, 1, 1, 2)

        self.retranslateUi(EmotionFinish)
        QtCore.QMetaObject.connectSlotsByName(EmotionFinish)

    def retranslateUi(self, EmotionFinish):
        EmotionFinish.setWindowTitle(QtWidgets.QApplication.translate("EmotionFinish", "EmotionTaskFinish", None, -1))
        self.titleLabel.setText(QtWidgets.QApplication.translate("EmotionFinish", "Finished!", None, -1))

