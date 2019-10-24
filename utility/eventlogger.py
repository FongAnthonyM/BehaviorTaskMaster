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
from abc import ABC, abstractmethod
import pathlib
import time
import datetime
import collections
import collections.abc
import csv

# Downloaded Libraries #
from bidict import frozenbidict
import h5py
import numpy as np

# Local Libraries #
from utility.iotriggers import AudioTrigger

########## Definitions ##########

# Classes #
class EventLoggerCSV(collections.UserList):
    def __init__(self, io_trigger=None, **kwargs):
        super().__init__(**kwargs)
        self.start_datetime = None
        self.start_time_counter = None
        self._path = None
        if io_trigger is None:
            self.io_trigger = AudioTrigger()
        else:
            self.io_trigger = io_trigger

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def set_time(self):
        self.start_datetime = datetime.datetime.now()
        self.start_time_counter = time.perf_counter()
        self.append({'Time': self.start_datetime, 'DeltaTime': 0, 'Type': 'TimeSet'})

    def create_event(self, _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {'Time': now, 'DeltaTime': seconds, 'Type': _type, **kwargs}

    def append(self, _type, **kwargs):
        if isinstance(_type, dict):
            super().append(_type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().append(event)

    def insert(self, i, _type, **kwargs):
        if isinstance(_type, dict):
            super().insert(i, _type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().insert(i, event)

    def clear(self):
        self.start_datetime = None
        self.start_time_counter = None
        self._path = None
        super().clear()

    def trigger(self):
        self.io_trigger.trigger()

    def trigger_event(self, **kwargs):
        self.trigger()
        self.append(_type='Trigger', **kwargs)

    def save_csv(self, path=None):
        if path is not None:
            self.path = path
        with self.path.open('w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"')
            for event in self.data:
                writer.writerow(self.event2list(event))

    @staticmethod
    def event2list(event):
        result = []
        for key, value in event.items():
            if isinstance(value, datetime.datetime):
                value = value.timestamp()
            result.append(key + ': ' + str(value))
        return result


class HDF5container:
    file_attrs = frozenbidict(type='Type')
    datasets = frozenbidict()

    def __init__(self, path=None, init=False):
        self._path = None
        self.path = path
        self.is_open = False
        self.is_updating = False
        self.cargs = {'compression': 'gzip', 'compression_opts': 4}
        self.default_datasets_parameters = {}

        self.h5_fobj = None

        if self.path.is_file():
            self.open()
            if not init:
                self.close()
        elif init:
            self.construct_file()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    def __getstate__(self):
        state = self.__dict__.copy()
        name = state['path'].as_posix()
        open = state['is_open']
        if open:
            fobj = state['h5_fobj']
            fobj.flush()
            fobj.close()
        state['h5_fobj'] = (name, open)
        return state

    def __setstate__(self, state):
        name, open = state['h5_fobj']
        state['h5_fobj'] = h5py.File(name.as_posix(), 'r+')
        if not open:
            state['h5_fobj'].close()
        self.__dict__.update(state)

    def __getitem__(self, item):
        op = self.is_open
        self.open()

        data = self.data[item]

        if not op:
            self.close()
        return data

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def __del__(self):
        self.close()

    def __getattribute__(self, item):
        if item in self.file_attr:
            return self._file_attribute(item)
        elif item in self.datasets:
            return self._dataset(item)
        else:
            return super().__getattribute__(item)

    def _file_attribute(self, item):
        _item = '_' + item
        op = self.is_open
        self.open()

        if self.file_attr[item] in self.h5_fobj.attrs and (super().__getattribute__(_item) is None or self.is_updating):
            setattr(self, _item, self.h5_fobj.attrs[self.file_attr[item]])

        if not op:
            self.close()
        return super().__getattribute__(_item)

    def _dataset(self, item):
        _item = '_' + item
        op = self.is_open
        self.open()

        if self.datasets[item] in self.h5_fobj and self.is_updating:
            setattr(self, _item, self.h5_fobj[self.file_attr[item]])

        if not op:
            self.close()

        return self._data

    def open(self, exc=False):
        if not self.is_open:
            try:
                self.h5_fobj = h5py.File(self.path.as_posix())
            except:
                if exc:
                    self.is_open = False
                else:
                    raise
            else:
                self.is_open = True
        return self.h5_fobj

    def close(self):
        if self.is_open:
            self.h5_fobj.flush()
            self.h5_fobj.close()
            self.is_open = False
        return not self.is_open

    def construct_file(self):
        self.h5_fobj = h5py.File(self.path.as_posix())
        self.h5_fobj.flush()

        return self.h5_fobj

    def construct_file_attrs(self, file_attrs, items=frozenbidict()):
        for key, value in file_attrs.items():
            if key in items:
                self.h5_fobj.attrs[value] = items[key]
            else:
                self.h5_fobj.attrs[value] = None
        self.h5_fobj.flush()

    def construct_datasets(self, datasets, parameters):
        for key, value in datasets.items():
            if key in parameters:
                self.__setattr__(key, self.h5_fobj.create_dataset(value, **parameters[key]))
            else:
                self.__setattr__(key, self.h5_fobj.create_dataset(value, **self.cargs))
        self.h5_fobj.flush()


class EventLogger(HDF5container):
    file_attrs = frozenbidict(type='Type')
    datasets = frozenbidict(events='Events')

    def __init__(self, path=None, init=False):
        super().__init__(path=path, init=init)

        self._type = 'EventLog'
        self.start_datetime = None
        self.start_time_counter = None

    def __repr__(self):
        return repr((self.start_datetime))

    def __len__(self):
        pass

    def __getitem__(self, item):
        op = self.is_open
        self.open()

        data = self.events[item]

        if not op:
            self.close()
        return data

    def set_time(self):
        self.start_datetime = datetime.datetime.now()
        self.start_time_counter = time.perf_counter()
        self.append({'Time': self.start_datetime, 'DeltaTime': 0, 'Type': 'TimeSet'})

    def create_event(self,  _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {'Time': now, 'DeltaTime': seconds, 'Type': _type, **kwargs}

    def get_event(self, item):
        pass

    def append(self, _type, **kwargs):
        if isinstance(_type, dict):
            super().append(_type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().append(event)

    def insert(self, i, _type, **kwargs):
        if isinstance(_type, dict):
            super().insert(i, _type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().insert(i, event)


class SubjectEventLogger(EventLogger):
    file_attrs = frozenbidict(type='Type', subject='Subject')
    datasets = frozenbidict(events='Events')
