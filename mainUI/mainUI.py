"""
.py

Last Edited:

Lead Author[s]: Anthony Fong
Contributor[s]:

Description:


Machine I/O
Input:
Output:

User I/O
Input:
Output:


"""
########################################################################################################################

########## Libraries, Imports, & Setup ##########

# Default Libraries #
import sys

# Downloaded Libraries #
from bidict import bidict
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QWidget

# Local Libraries #
from mainUI.mainmenu import Ui_MainMenu


########## Definitions ##########

# Classes #
class MainMenuWidget(QWidget):
    def __init__(self):
        super(MainMenuWidget, self).__init__()
        self.items = dict()
        self.double_click_action = self.default_double_click
        self.selected_item = None
        self.selected_action = self.default_selected

        self.ui = Ui_MainMenu()
        self.ui.setupUi(self)

        self.ui.taskList.doubleClicked.connect(self.double_click)
        self.ui.selectButton.clicked.connect(self.select)
        self.ui.cancelButton.clicked.connect(self.cancel)

        self.list_model = QtGui.QStandardItemModel()
        self.ui.taskList.setModel(self.list_model)

    def double_click(self, index):
        self.double_click_action(index)

    def select(self):
        _, self.selected_item, _ = self.current_item()
        self.selected_action()

    def cancel(self):
        sys.exit()

    def default_double_click(self, index):
        print(index.row())

    def default_selected(self):
        print(self.selected_item)

    def add_item(self, text, name, index=-1):
        item = QtGui.QStandardItem(text)
        item.setEditable(False)
        item.setDragEnabled(False)
        item.setDropEnabled(False)
        if index == -1:
            index = self.list_model.rowCount()
            self.list_model.appendRow(item)
        else:
            self.list_model.insertRow(index, item)
        self.items[name] = index
        self.items[index] = name

    def remove_item(self, w):
        _, _, i = self.find(w)
        self.removeRow(i)

    def find_item(self, item):
        if not isinstance(item, int):
            index = self.items[item]
        else:
            index = item
        q_index = self.list_model.createIndex(index, 0)
        item = self.list_model.itemFromIndex(q_index)
        name = self.items[index]
        return item, name, index

    def current_item(self):
        index = self.ui.taskList.selectedIndexes()[0]
        number = index.row()
        name = self.items[number]
        item = self.list_model.itemFromIndex(index)
        return item, name, number




if __name__ == "__main__":
    app = QApplication(sys.argv)

    ex = MainMenuWidget()

    ex.show()

    sys.exit(app.exec_())