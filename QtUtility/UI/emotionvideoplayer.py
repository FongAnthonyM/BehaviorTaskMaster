# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionvideoplayer.ui',
# licensing of 'emotionvideoplayer.ui' applies.
#
# Created: Fri Oct 11 13:48:36 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionVideoPlayer(object):
    def setupUi(self, EmotionVideoPlayer):
        EmotionVideoPlayer.setObjectName("EmotionVideoPlayer")
        EmotionVideoPlayer.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionVideoPlayer)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(50, 50, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 1)

        self.retranslateUi(EmotionVideoPlayer)
        QtCore.QMetaObject.connectSlotsByName(EmotionVideoPlayer)

    def retranslateUi(self, EmotionVideoPlayer):
        EmotionVideoPlayer.setWindowTitle(QtWidgets.QApplication.translate("EmotionVideoPlayer", "EmotionVideoPlayer", None, -1))

