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
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QApplication, QAction

# Local Libraries #
from stackedmain.stackedmain import MainWindow
from mainUI.mainUI import MainMenuWidget
from emotionTask.emotiontask import EmotionTask


########## Definitions ##########

# Classes #
class BehaviorTaskWindow(MainWindow):
    def __init__(self):
        super(BehaviorTaskWindow, self).__init__()
        self.tasks = dict()
        self.selected_task = None
        self.default_widget = "MainMenu"

        self.main_menu = MainMenuWidget()
        self.main_menu.selected_action = self.select_action
        self.widget_stack.add(self.main_menu, "MainMenu")

        self.fullscreenAction = QAction("FullScreen", self)
        self.fullscreenAction.setShortcut(QKeySequence.FullScreen)
        self.fullscreenAction.triggered.connect(self.fullscreen_action)
        self.addAction(self.fullscreenAction)

    def add_task(self, task, name, text):
        self.tasks[name] = task
        self.main_menu.add_item(text, name)

    def select_action(self):
        self.selected_task = self.tasks[self.main_menu.selected_item]
        self.selected_task.load_task(self.widget_stack)
        self.selected_task.setup_task()

    def fullscreen_action(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BehaviorTaskWindow()
    window.add_task(EmotionTask(window), "EmotionItem", "Emotion Task")
    window.add_task(EmotionTask(window), "NotEmotionItem", "Not Emotion Task")

    window.show()

    sys.exit(app.exec_())