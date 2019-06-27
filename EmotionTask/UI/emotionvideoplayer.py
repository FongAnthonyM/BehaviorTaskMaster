# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emotionvideoplayer.ui',
# licensing of 'emotionvideoplayer.ui' applies.
#
# Created: Wed Jun 26 15:09:11 2019
#      by: pyside2-uic  running on PySide2 5.12.4
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EmotionVideoPlayer(object):
    def setupUi(self, EmotionVideoPlayer):
        EmotionVideoPlayer.setObjectName("EmotionVideoPlayer")
        EmotionVideoPlayer.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(EmotionVideoPlayer)
        self.gridLayout.setObjectName("gridLayout")

        self.retranslateUi(EmotionVideoPlayer)
        QtCore.QMetaObject.connectSlotsByName(EmotionVideoPlayer)

    def retranslateUi(self, EmotionVideoPlayer):
        EmotionVideoPlayer.setWindowTitle(QtWidgets.QApplication.translate("EmotionVideoPlayer", "EmotionVideoPlayer", None, -1))

