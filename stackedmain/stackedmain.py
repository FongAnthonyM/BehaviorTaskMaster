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
from PySide2.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout

# Local Libraries #


########## Definitions ##########

# Classes #
class WidgetStack(QStackedWidget):
    def __init__(self, parent):
        super(WidgetStack, self).__init__(parent)
        self.keys = dict()

    def __len__(self):
        return self.count()

    def __getitem__(self, item):
        w, _, _ = self.find_stacked(item)
        return w

    def add(self, w, name, i=-1):
        index = self.insertWidget(i, w)
        self.keys[name] = w
        self.keys[w] = name
        return index

    def remove(self, w):
        w, n, _ = self.find_stacked(w)
        self.removeWidget(w)
        del self.keys[n]
        del self.keys[w]

    def find_stacked(self, w):
        if isinstance(w, str):
            w = self.keys[w]
        elif isinstance(w, int):
            w = self.widget(w)
        name = self.keys[w]
        index = self.indexOf(w)
        return w, name, index

    def current(self):
        index = self.currentIndex()
        return self.find_stacked(index)

    def set(self, w):
        _, _, i = self.find_stacked(w)
        self.setCurrentIndex(i)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.widget_stack = WidgetStack(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget_stack)
        self.setLayout(self.layout)

        self.setCentralWidget(self.widget_stack)
