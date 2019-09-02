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

# Downloaded Libraries #
from PySide2.QtWidgets import QMainWindow, QHBoxLayout

# Local Libraries #
from QtUtility.widgetstack import WidgetStack


########## Definitions ##########

# Classes #
class MainStackedWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_stack = WidgetStack(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget_stack)
        self.setLayout(self.layout)

        self.setCentralWidget(self.widget_stack)

