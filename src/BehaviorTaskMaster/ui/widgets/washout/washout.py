# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'washout.ui',
# licensing of 'washout.ui' applies.
#
# Created: Fri Oct 11 11:20:23 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Washout(object):
    def setupUi(self, Washout):
        Washout.setObjectName("WashoutContainer")
        Washout.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(Washout)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(150, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(Washout)
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
        self.colorSpacer = QtWidgets.QPushButton(Washout)
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

        self.retranslateUi(Washout)
        QtCore.QMetaObject.connectSlotsByName(Washout)

    def retranslateUi(self, Washout):
        Washout.setWindowTitle(QtWidgets.QApplication.translate("WashoutContainer", "WashoutContainer", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("WashoutContainer", "X", None, -1))
