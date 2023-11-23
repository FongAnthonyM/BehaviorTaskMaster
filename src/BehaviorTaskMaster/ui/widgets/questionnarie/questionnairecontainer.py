""" questionnairecontainer.py
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
import pathlib

# Third-Party Packages #

# Local Packages #
from ..base import BaseWidgetContainer
from .questionnairewidget import QuestionnaireWidget


# Definitions #
# Classes #
class QuestionnaireContainer(BaseWidgetContainer):
    def __init__(self, name="Questionnaire", path=None, events=None, init=False):
        super().__init__(name, init)
        BaseWidgetContainer.__init__(self, name, init)
        self._next_action = self.next_question
        self._finish_action = None
        self._previous_action = self.previous_question
        self._back_action = None
        self._answer_action = self.answer_selected

        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent
        else:
            self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    @property
    def next_action(self):
        try:
            out = self.widget.next_action
        except AttributeError:
            out = self._next_action
        return out

    @next_action.setter
    def next_action(self, value):
        self._next_action = value
        if self.widget is not None:
            self.widget.next_action = value

    @property
    def finish_action(self):
        try:
            out = self.widget.finish_action
        except AttributeError:
            out = self._finish_action
        return out

    @finish_action.setter
    def finish_action(self, value):
        self._finish_action = value
        if self.widget is not None:
            self.widget.finish_action = value

    @property
    def previous_action(self):
        try:
            out = self.widget.previous_action
        except AttributeError:
            out = self._previous_action
        return out

    @previous_action.setter
    def previous_action(self, value):
        self._previous_action = value
        if self.widget is not None:
            self.widget.previous_action = value

    @property
    def back_action(self):
        try:
            out = self.widget.back_action
        except AttributeError:
            out = self._back_action
        return out

    @back_action.setter
    def back_action(self, value):
        self._back_action = value
        if self.widget is not None:
            self.widget.back_action = value

    @property
    def answer_action(self):
        try:
            out = self.widget.answer_action
        except AttributeError:
            out = self._answer_action
        return out

    @answer_action.setter
    def answer_action(self, value):
        self._answer_action = value
        if self.widget is not None:
            self.widget.answer_action = value

    def construct_widget(self):
        self.widget = QuestionnaireWidget(self._next_action, self._finish_action, self._previous_action,
                                          self._back_action, self._answer_action)

    def run(self, path=None, next_action=None, finish_action=None, previous_action=None, back_action=None,
            answer_action=None, ):
        if path is not None:
            self.path = path
        if next_action is not None:
            self.next_action = next_action
        if finish_action is not None:
            self.finish_action = finish_action
        if previous_action is not None:
            self.previous_action = previous_action
        if back_action is not None:
            self.back_action = back_action
        if answer_action is not None:
            self.answer_action = answer_action

        if self.path.as_posix() == '.':
            event = {"type_": 'Questionnaire', 'SubType': 'NoFile'}
            self.widget.finish_action(event=event, caller=self)
        else:
            self.widget.load_file(self.path)
            event = {'SubType': 'Start'}
            super().run()
            # self.events.trigger_event(**event)
            self.events.append(type_="Questionnaire", **event)

    def next_question(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_next(event=event, caller=caller)
        t_event = {'SubType': 'Next', 'Question': event['Question']}
        # self.events.trigger_event(**event)
        self.events.append(type_="Questionnaire", **t_event)

    def previous_question(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_previous(event=event, caller=caller)
        t_event = {'SubType': 'Previous', 'Question': event['Question']}
        # self.events.trigger_event(**event)
        self.events.append(type_="Questionnaire", **event)

    def answer_selected(self, event=None, caller=None):
        self.events.append(**event)
