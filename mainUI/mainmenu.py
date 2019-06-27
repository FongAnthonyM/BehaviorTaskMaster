# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainmenu.ui',
# licensing of 'mainmenu.ui' applies.
#
# Created: Mon Jun 24 09:49:11 2019
#      by: pyside2-uic  running on PySide2 5.12.4
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainMenu(object):
    def setupUi(self, MainMenu):
        MainMenu.setObjectName("MainMenu")
        MainMenu.resize(800, 600)
        self.gridLayout = QtWidgets.QGridLayout(MainMenu)
        self.gridLayout.setObjectName("gridLayout")
        self.cancelButton = QtWidgets.QPushButton(MainMenu)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
        self.gridLayout.addWidget(self.cancelButton, 5, 3, 1, 1)
        self.selectButton = QtWidgets.QPushButton(MainMenu)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.selectButton.setFont(font)
        self.selectButton.setObjectName("selectButton")
        self.gridLayout.addWidget(self.selectButton, 5, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.titleLable = QtWidgets.QLabel(MainMenu)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLable.sizePolicy().hasHeightForWidth())
        self.titleLable.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.titleLable.setFont(font)
        self.titleLable.setTextFormat(QtCore.Qt.AutoText)
        self.titleLable.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLable.setObjectName("titleLable")
        self.gridLayout.addWidget(self.titleLable, 1, 1, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 6, 1, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 2, 1, 1, 3)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem4, 4, 1, 1, 3)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 1, 0, 5, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem6, 1, 4, 5, 1)
        self.taskList = QtWidgets.QListView(MainMenu)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.taskList.setFont(font)
        self.taskList.setObjectName("taskList")
        self.gridLayout.addWidget(self.taskList, 3, 1, 1, 3)

        self.retranslateUi(MainMenu)
        QtCore.QMetaObject.connectSlotsByName(MainMenu)

    def retranslateUi(self, MainMenu):
        MainMenu.setWindowTitle(QtWidgets.QApplication.translate("MainMenu", "BehaviorTaskMasterMenu", None, -1))
        self.cancelButton.setText(QtWidgets.QApplication.translate("MainMenu", "Cancel", None, -1))
        self.selectButton.setText(QtWidgets.QApplication.translate("MainMenu", "Select", None, -1))
        self.titleLable.setText(QtWidgets.QApplication.translate("MainMenu", "Task Selection", None, -1))

