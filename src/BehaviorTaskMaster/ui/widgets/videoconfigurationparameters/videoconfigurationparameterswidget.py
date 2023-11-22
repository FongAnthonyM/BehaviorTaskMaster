""" videoConfigurationParameterswidget.py
Description:
"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
import sys
import pathlib
import copy
import datetime

# Third-Party Packages #
from PySide2 import QtGui, QtWidgets, QtMultimedia
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QWidget, QAction, QFileDialog, QAbstractItemView, QStyle

# Local Packages #
from .videoconfigurationparameters import Ui_VideoConfigurationParameters


# Definitions #
# Constants #
START_DIR = ""


# Classes #
class VideoConfigurationParametersWidget(QWidget):
    header = ('Video', 'Configurations', 'Video Path', 'Configurations Path')
    v_types = ('*.avi', '*.mp4', '*.ogg', '*.qt', '*.wmv', '*.yuv')
    q_types = ('*.toml',)

    def __init__(self):
        super().__init__()
        self.ok_action = self.default_ok
        self.back_action = self.default_back

        self._parameters = {}
        self.subject = []
        self.session = []
        self.blocks = []

        self.ui = Ui_VideoConfigurationParameters()
        self.ui.setupUi(self)

        self.list_model = None
        self._construct_video_list()

        self.deleteAction = None
        self._construct_deleteAction()

        self.okAction = None
        self._construct_okAction()

        self._construct_backAction()

    @property
    def parameters(self):
        self._parameters['subject'] = self.subject
        self._parameters['session'] = self.session
        self._parameters['blocks'] = self.blocks
        return self._parameters

    @property
    def static_parameters(self):
        self._parameters['blocks'] = self.blocks
        self._parameters['loops'] = self.loops
        self._parameters['randomize'] = self.randomize
        return copy.deepcopy(self._parameters)

    def _construct_video_list(self):
        self.list_model = QtGui.QStandardItemModel(0, 4)
        self.list_model.setHorizontalHeaderLabels(self.header)
        self.ui.videoList.setModel(self.list_model)
        self.ui.videoList.setDragDropMode(QAbstractItemView.InternalMove)
        self.ui.videoList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.videoList.setColumnWidth(0, 200)
        self.ui.videoList.setColumnWidth(1, 200)
        self.ui.videoList.setColumnWidth(2, 100)
        self.ui.videoList.setColumnWidth(3, 100)

        self.ui.videoList.doubleClicked.connect(self.double_click)
        self.ui.addVideoButton.clicked.connect(self.add_videos)
        self.ui.addConfigurationsButton.clicked.connect(self.add_configurations)
        self.ui.videoDirectory.clicked.connect(self.video_directory)
        self.ui.configurationDirectory.clicked.connect(self.configuration_directory)
        self.ui.deleteLastButton.clicked.connect(self.delete_last)
        self.ui.clearAll.clicked.connect(self.clear_all)

    def _construct_deleteAction(self):
        self.deleteAction = QAction("delete", self)
        self.deleteAction.setShortcut(QKeySequence.Delete)
        self.deleteAction.triggered.connect(self.delete_key)
        self.addAction(self.deleteAction)

    def _construct_okAction(self):
        self.okAction = QAction("OK", self)
        self.okAction.setShortcut(QKeySequence("Shift+Return"))
        self.okAction.triggered.connect(self.ok_action)
        self.addAction(self.okAction)

        self.ui.okButton.clicked.connect(self.ok)

    def _construct_backAction(self):
        self.ui.backButton.clicked.connect(self.back)

    def double_click(self, index):
        if index.column() in (0, 2):
            self.change_video(index.row())
        elif index.column() in (1, 3):
            self.change_configuration(index.row())

    def delete_key(self):
        fw = self.focusWidget()
        if fw is self.ui.videoList:
            self.delete_video()

    def find_last_row(self, item=''):
        end = self.list_model.rowCount()
        index = -1
        for i in reversed(range(0, end)):
            video = self.list_model.item(i, 0).text()
            configuration = self.list_model.item(i, 1).text()
            if item == 'video':
                text = video
            elif item == 'configuration':
                text = configuration
            elif item == 'video&configuration':
                text = video + configuration
            else:
                break
            if text == '':
                index = i
            else:
                break
        return index

    def add_item(self, video='', configuration='', index=-1):
        # Make Row Objects
        video_name = QtGui.QStandardItem(pathlib.Path(video).name)
        configurations_name = QtGui.QStandardItem(pathlib.Path(configuration).name)
        videos = QtGui.QStandardItem(video)
        configurations = QtGui.QStandardItem(configuration)

        # Row Settings
        video_name.setEditable(False)
        video_name.setDragEnabled(True)
        video_name.setDropEnabled(False)
        configurations_name.setEditable(False)
        configurations_name.setDropEnabled(False)
        videos.setEditable(False)
        videos.setDropEnabled(False)
        configurations.setEditable(False)

        if index == -1:
            index = self.list_model.rowCount()
            self.list_model.appendRow(video_name)
        else:
            self.list_model.insertRow(index, video_name)
        self.list_model.setItem(index, 1, configurations_name)
        self.list_model.setItem(index, 2, videos)
        self.list_model.setItem(index, 3, configurations)

    def edit_item(self, index=None, video='', configuration=''):
        if index is None:
            item = ''
            if video != '' and configuration != '':
                item = 'video&configuration'
            elif video != '':
                item = 'video'
            elif configuration != '':
                item = 'configuration'
            index = self.find_last_row(item=item)

        videos_name = self.list_model.item(index, 0)
        configurations_name = self.list_model.item(index, 1)
        videos = self.list_model.item(index, 2)
        configurations = self.list_model.item(index, 3)

        if video != '':
            videos_name.setText(pathlib.Path(video).name)
            videos.setText(video)
        if configuration != '':
            configurations_name.setText(pathlib.Path(configuration).name)
            configurations.setText(configuration)

    def change_video(self, row):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            video_name = self.list_model.item(row, 0)
            videos = self.list_model.item(row, 2)
            v = dialog.selectedFiles()[0]
            video_name.setText(pathlib.Path(v).name)
            videos.setText(v)

    def change_configuration(self, row):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Configuration", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            configurations_name = self.list_model.item(row, 1)
            configurations = self.list_model.item(row, 3)
            q = dialog.selectedFiles()[0]
            configurations_name.setText(pathlib.Path(q).name)
            configurations.setText(q)

    def add_videos(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            video_names = dialog.selectedFiles()
            for video in video_names:
                last = self.find_last_row('video')
                if last == -1:
                    self.add_item(video=video)
                else:
                    self.edit_item(index=last, video=video)

    def add_configurations(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Configurations", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            configuration_names = dialog.selectedFiles()
            for configuration in configuration_names:
                last = self.find_last_row('configuration')
                if last == -1:
                    self.add_item(configuration=configuration)
                else:
                    self.edit_item(index=last, configuration=configuration)

    def video_directory(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Video Directory", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            dir_names = dialog.selectedFiles()
            dir_path = pathlib.Path(dir_names[0])
            files = []
            for ext in self.v_types:
                files.extend(dir_path.glob(ext))
            for video in files:
                last = self.find_last_row('video')
                if last == -1:
                    self.add_item(video=str(video))
                else:
                    self.edit_item(index=last, video=str(video))

    def configuration_directory(self):
        start_dir = pathlib.Path.home()
        other = start_dir.joinpath(START_DIR)
        if other.is_dir():
            start_dir = other
        dialog = QFileDialog(self, caption="Open Configurations Directory", directory=start_dir.as_posix())
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            dir_names = dialog.selectedFiles()
            dir_path = pathlib.Path(dir_names[0])
            files = []
            if len(self.q_types) < 1 or '*' in self.q_types:
                files = dir_path.iterdir()
            else:
                for ext in self.q_types:
                    files.extend(dir_path.glob(ext))
            for configuration in files:
                last = self.find_last_row('configuration')
                if last == -1:
                    self.add_item(configuration=str(configuration))
                else:
                    self.edit_item(index=last, configuration=str(configuration))

    def delete_last(self):
        last = self.list_model.rowCount() - 1
        self.list_model.removeRow(last)

    def delete_video(self):
        items = self.ui.videoList.selectedIndexes()
        indices = []
        for i in items:
            indices.append(i.row())
        indices.sort(reverse=True)
        for i in indices:
            self.list_model.removeRow(i)

    def clear_all(self):
        self.list_model.clear()
        self.list_model.setHorizontalHeaderLabels(self.header)
        self.ui.videoList.setColumnWidth(0, 200)
        self.ui.videoList.setColumnWidth(1, 200)
        self.ui.videoList.setColumnWidth(2, 100)
        self.ui.videoList.setColumnWidth(3, 100)

    def evaluate(self):
        self.subject.clear()
        self.session.clear()
        self.blocks.clear()
        self.subject.append(self.ui.subjectIDEdit.text())
        self.session.append(self.ui.blockEdit.text())
        for i in range(0, self.list_model.rowCount()):
            video = pathlib.Path(self.list_model.item(i, 2).text())
            configuration = pathlib.Path(self.list_model.item(i, 3).text())
            washout = self.ui.washoutBox.value()
            self.blocks.append({'video': video, 'configurations': configuration, 'washout': washout})

    def ok(self):
        self.evaluate()
        self.ok_action()

    def default_ok(self):
        print("Not Connected")

    def back(self):
        self.back_action()

    def default_back(self):
        sys.exit()
