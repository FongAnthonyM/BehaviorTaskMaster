""" ratingtask.py
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
import toml

# Local Packages #
from ....utility.iotriggers import AudioTrigger
from ....utility.eventlogger import SubjectEventLogger
from ....utility.tcsdevice import TCSDevice
from ....ui.windows import TaskWindow
from ....ui.widgets import BaseWidgetContainer, WidgetContainerSequencer
from ....ui.widgets import InstructionsContainer, WashoutContainer, FinishContainer, VideoPlayerContainer, RatingContainer
from ....ui.widgets import VideoPlayerControlContainer
from ....ui.widgets import VideoConfigurationParametersContainer


# Definitions #
# Classes #
class TemperatureVideoPlayerContainer(VideoPlayerContainer):
    def __init__(self, name="VideoPlayer", source="path", path=None, url=None, events=None, device=None, init=False):
        self.device = device
        self.temperature_configs = None
        self.start_frame = 0
        self.temp_index = 0

        super().__init__(name=name, source=source, path=path, url=url, events=events, init=init)

    def __del__(self):
        if self.device is not None:
            self.device.close()

    def load_config(self):
        if self.config_path.as_posix() != '.':
            self.temperature_configs = toml.load(self.config_path)["TCS"]
            self.start_frame = self.temperature_configs[0]["start_frame"]
            self.temp_index = 0

    def frame_process(self, frame=None, number=None, event=None, caller=None, **kwargs):
        # could use frame metadata if it exists: print(frame.metaData(str_name))
        if number == self.start_frame:
            print(f"Temp Start:{datetime.datetime.now().strftime('%H:%M:%S.%f')}")
            temperature_config = self.temperature_configs[0]
            self.device.set_quiet()
            self.device.set_baseline(temperature_config["baseline"])
            self.device.set_durations(temperature_config["durations"])
            self.device.set_ramp_speed(temperature_config["ramp_speed"])
            self.device.set_return_speed(temperature_config["return_speed"])
            self.device.set_temperatures(temperature_config["temperatures"])
            self.device.stimulate()

            event = {
                "type_": "Temperature_Start",
                "frame_start": temperature_config["start_frame"],
                "baseline": temperature_config["baseline"],
            }
            event.update({f"duration_{i}": d for i, d in enumerate(temperature_config["durations"])})
            event.update({f"ramp_speed_{i}": r for i, r in enumerate(temperature_config["ramp_speed"])})
            event.update({f"return_speed_{i}": r for i, r in enumerate(temperature_config["return_speed"])})
            event.update({f"temperature_{i}": r for i, r in enumerate(temperature_config["temperatures"])})

            self.events.append(**event)
            if self.temp_index < len(self.temperature_configs) - 1:
                self.temp_index += 1
                self.start_frame = self.temperature_configs[self.temp_index]["start_frame"]


class TemperatureRatingTask:
    EXPERIMENT_NAME = "Pain Temperature Rating"

    def __init__(self, parent=None, stack=None, r_widget=None):
        self.parent = parent
        self.widget_stack = stack
        self.return_widget = r_widget

        # self.trigger = AudioTrigger()
        # self.trigger.audio_device.device = 3
        # self.trigger.add_square_wave('square_wave', amplitude=5, samples=22000, channels=1)
        # self.trigger.current_waveform = 'square_wave'

        self.task_window = TaskWindow()
        self.events = SubjectEventLogger(
            # io_trigger=self.trigger,
        )
        
        self.sequencer = WidgetContainerSequencer()
        self.task_window.sequencer = self.sequencer

        self.parameters = VideoConfigurationParametersContainer()
        self.control = VideoPlayerControlContainer(events=self.events, x_name=self.EXPERIMENT_NAME, path=pathlib.Path(__file__).parent)
        self.instructions = InstructionsContainer(path=pathlib.Path(__file__).parent.joinpath('instructions.txt'), events=self.events)
        self.video_player = TemperatureVideoPlayerContainer(events=self.events, device=TCSDevice())
        self.questionnaire = RatingContainer(events=self.events)
        self.washout = WashoutContainer(events=self.events)
        self.finished = FinishContainer(events=self.events)

        self.block_widgets = {'instructions': self.instructions, 'video_player': self.video_player,
                              'questionnaire': self.questionnaire, 'washout': self.washout, 'finish': self.finished}
        self.sequence_order = ['instructions', '*block*', 'washout', 'finish']
        self.block_order = ['washout', 'video_player', 'questionnaire']

    def load_task(self, stack=None):
        if stack is not None:
            self.widget_stack = stack

        if self.return_widget is None:
            _, self.return_widget, _ = self.widget_stack.current()

        self.widget_stack.load(self.parameters)
        self.widget_stack.load(self.control)

        self.task_window.load(self.instructions)
        self.task_window.load(self.washout)
        self.task_window.load(self.video_player)
        self.task_window.load(self.questionnaire)
        self.task_window.load(self.finished)

        self.control.task_window = self.task_window
        self.control.sequencer = self.sequencer
        self.control.sequence_order = self.sequence_order
        self.control.parameters = self.parameters.parameters
        self.control.block_widgets = self.block_widgets
        self.control.player = self.video_player

    def unload_task(self, back=True, clear_widget=False):
        if back:
            self.widget_stack.set(self.return_widget)

        self.widget_stack.unload(self.parameters, back=False, clear_widget=clear_widget)
        self.widget_stack.unload(self.control, back=False, clear_widget=clear_widget)

        self.task_window.close()
        self.task_window.unload(self.instructions, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.washout, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.video_player, back=False, clear_widget=clear_widget)
        self.task_window.unload(self.questionnaire, back=False, clear_widget=clear_widget)

    def setup_task(self):
        self.parameters.run(self.control_task, self.unload_task)

    def control_task(self):
        self.control.run(self.parameters.run)
