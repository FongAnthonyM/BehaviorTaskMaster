#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" emotionwidgets.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2019, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #
import pathlib

# Downloaded Libraries #
from PySide2.QtCore import QUrl

# Local Libraries #
from ..QtUtility.utilitywidgets import WidgetContainer
from ..QtUtility.taskwidgets import InstructionsWidget, WashoutWidget, QuestionnaireWidget, FinishWidget, VideoPlayerWidget, QuestionnaireImageWidget
from ..QtUtility.ratingwidget import RatingWidget


# Definitions #
# Classes #
class EmotionInstructions(WidgetContainer):
    def __init__(self, name="Instructions", path=None, events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.ok_action = None
        self.back_action = self.remove_from_stack

        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('instructions.txt')
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

    def construct_widget(self):
        self.widget = InstructionsWidget()

    def run(self, ok_action=None, back_action=None):
        if ok_action is not None:
            self.ok_action = ok_action
        if back_action is not None:
            self.back_action = back_action

        self.widget.ok_action = self.ok_action
        self.widget.back_action = self.back_action
        self.load_text()
        event = {'SubType': 'InstructionsStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def load_text(self):
        with self.path.open('r') as file:
            self.widget.text = file.read()
        self.widget.set_text()


class EmotionWashout(WidgetContainer):
    def __init__(self, name="Washout", events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self.timer_action = None

        self.events = events

        self.milliseconds = 0
        self.font_size = 100
        self.text = "X"

    def construct_widget(self):
        self.widget = WashoutWidget()

    def run(self, milliseconds=None, timer_action=None):
        if milliseconds is not None:
            self.milliseconds = milliseconds
        if timer_action is not None:
            self.timer_action = timer_action

        self.widget.timer_action = self.timer_action
        self.widget.milliseconds = self.milliseconds
        event = {'SubType': 'WashoutStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)
        self.widget.start()

    def setup(self):
        self.widget.milliseconds = self.milliseconds
        self.widget.set_text(self.text)
        self.widget.set_font_size(self.font_size)


class EmotionQuestionnaire(WidgetContainer):
    def __init__(self, name="Questionnaire", path=None, events=None, init=False):
        super().__init__(name, init)
        WidgetContainer.__init__(self, name, init)
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
            event = {'_type': 'Questionnaire', 'SubType': 'NoFile'}
            self.widget.finish_action(event=event, caller=self)
        else:
            self.widget.load_file(self.path)
            event = {'SubType': 'QuestionsStart'}
            super().run()
            # self.events.trigger_event(**event)
            self.events.append(type_="General", **event)

    def next_question(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_next(event=event, caller=caller)
        event = {'SubType': 'QuestionNext', 'Question': event['Question']}
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def previous_question(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_previous(event=event, caller=caller)
        t_event = {'SubType': 'QuestionPrevious', 'Question': event['Question']}
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def answer_selected(self, event=None, caller=None):
        self.events.append(**event)


class EmotionQuestionnaireImage(EmotionQuestionnaire):
    def construct_widget(self):
        self.widget = QuestionnaireImageWidget(self._next_action, self._finish_action, self._previous_action, self._back_action, self._answer_action)

class EmotionRating(WidgetContainer):
    def __init__(self, name="Rating", path=None, events=None, init=False):
        super().__init__(name, init)
        WidgetContainer.__init__(self, name, init)
        self._next_action = self.next_rating
        self._finish_action = None
        self._previous_action = self.previous_rating
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
        self.widget = RatingWidget(self._next_action, self._finish_action, self._previous_action,
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
            event = {'_type': 'Rating', 'SubType': 'NoFile'}
            self.widget.finish_action(event=event, caller=self)
        else:
            self.widget.load_file(self.path)
            event = {'SubType': 'RatingsStart'}
            super().run()
            # self.events.trigger_event(**event)
            self.events.append(type_="General", **event)

    def next_rating(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_next(event=event, caller=caller)
        event = {'SubType': 'RatingNext', 'Ratings': event['Ratings']}
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def previous_rating(self, event=None, caller=None):
        self.events.append(**event)
        self.widget.default_previous(event=event, caller=caller)
        t_event = {'SubType': 'RatingPrevious', 'Ratings': event['Ratings']}
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)

    def answer_selected(self, event=None, caller=None):
        self.events.append(**event)


class EmotionFinish(WidgetContainer):
    def __init__(self, name="Finish", path=None, events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self._run_action = self.finish_process

        self.events = events

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('UI', 'end.jpg')
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
    def run_action(self):
        try:
            out = self.widget.run_action
        except AttributeError:
            out = self._run_action
        return out

    @run_action.setter
    def run_action(self, value):
        self._run_action = value
        if self.widget is not None:
            self.widget.run_action = value

    def construct_widget(self):
        self.widget = FinishWidget()
        self.widget.run_action = self._run_action

    def run(self, path=None):
        if path is not None:
            self.path = path
        self.widget.load_file(self.path)
        event = {'SubType': 'Finished'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)
        self.widget.start()

    def finish_process(self, event=None, caller=None):
        self.events.append(**event)
        self.events.close()


class EmotionVideoPlayer(WidgetContainer):
    def __init__(self, name="VideoPlayer", source="path", path=None, url=None, events=None, init=False):
        WidgetContainer.__init__(self, name, init)
        self._frame_action = self.frame_process
        self._finish_action = None

        self.events = events

        self._media_player = None
        self.source = source

        self._path = None
        if path is None:
            self._path = pathlib.Path(__file__).parent.joinpath('emotionTask', 'default.mp4')
        else:
            self.path = path

        self._url = None
        if url is None:
            self._url = QUrl("http://clips.vorwaerts-gmbh.de/VfE_html5.mp4")
        else:
            self.url = url

    @property
    def media_player(self):
        try:
            out = self.widget.mediaPlayer
        except AttributeError:
            out = self._media_player
        return out

    @media_player.setter
    def media_player(self, value):
        self._media_player = value
        if self.widget is not None:
            self.widget.mediaPlayer = value

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
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if isinstance(value, QUrl) or value is None:
            self._url = value
        else:
            self._url = QUrl(value)

    @property
    def video(self):
        if self.source == "url":
            return self._url
        else:
            return self._path

    @property
    def frame_action(self):
        try:
            out = self.widget.frame_action
        except AttributeError:
            out = self._frame_action
        return out

    @frame_action.setter
    def frame_action(self, value):
        self._frame_action = value
        if self.widget is not None:
            self.widget.frame_action = value

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

    def construct_widget(self):
        self.widget = VideoPlayerWidget()
        self.widget.frame_action = self._frame_action
        self.widget.finish_action = self._finish_action

    def run(self, source="path", path=None, url=None, frame_action=None, finish_action=None):
        if source is not None:
            self.source = source
        if path is not None:
            self.path = path
        if url is not None:
            self.url = url
        if frame_action is not None:
            self.frame_action = frame_action
        if finish_action is not None:
            self.finish_action = finish_action

        self.load_video()
        event = {'SubType': 'VideoStart'}
        super().run()
        # self.events.trigger_event(**event)
        self.events.append(type_="General", **event)
        self.widget.play()

    def load_video(self, video=None):
        if video is None:
            self.widget.set_video(self.video)
        else:
            self.widget.set_video(video)

    def frame_process(self, frame=None, number=None, event=None, caller=None):
        # could use frame metadata if is exists: print(frame.metaData(str_name))
        self.events.append(**event)
        # print(self.events[-1])
