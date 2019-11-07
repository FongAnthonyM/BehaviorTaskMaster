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
from warnings import warn
import csv

# Downloaded Libraries #
from bidict import bidict
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
    container_type = "Abstract"
    version = "0.0.0"

    def __init__(self, path=None, init=False):
        self._path = None
        self.path = path
        self.is_open = False
        self.is_updating = False
        self.cargs = {'compression': 'gzip', 'compression_opts': 4}
        self.default_datasets_parameters = self.cargs.copy()

        self._file_attrs = set('FileType', 'Version')
        self._datasets = set()

        self.h5_fobj = None

        if init:
            self.construct()

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
        open_state = state['is_open']
        if open:
            fobj = state['h5_fobj']
            fobj.flush()
            fobj.close()
        state['h5_fobj'] = (name, open_state)
        return state

    def __setstate__(self, state):
        name, open_state = state['h5_fobj']
        state['h5_fobj'] = h5py.File(name.as_posix(), 'r+')
        if not open_state:
            state['h5_fobj'].close()
        self.__dict__.update(state)

    def __getattribute__(self, item):
        if item in self._file_attrs:
            return self.get_file_attribute(item)
        elif item in self._datasets:
            return self.get_dataset(item)
        else:
            return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self._file_attrs:
            self.set_file_attribute(key, value)
        elif key in self._datasets:
            self.set_dataset(key, value)
        else:
            return super().__setattr__(key, value)

    def __getitem__(self, item):
        if item in self._datasets:
            data = self.get_dataset(item)
        else:
            raise KeyError(item)
        return data

    def __setitem__(self, key, value):
        self.set_dataset(key, value)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def __del__(self):
        self.close()

    def construct(self, _open=False, **kwargs):
        if self.path.is_file():
            self.open(validate=True, )**kwargs
            if not _open:
                self.close()
        else:
            self.construct_file(_open=_open)

    def construct_file(self, _open=False):
        self.open()
        self.construct_file_attributes()
        self.construct_file_datasets()
        if _open:
            return self.h5_fobj
        else:
            self.close()
            return None

    def construct_file_attributes(self, value=None):
        if len(self._file_attrs.intersection(self._datasets)) > 0:
            warn('Attribute name already exists', stacklevel=2)

        op = self.is_open
        self.open()
        for key in self._file_attrs:
            _key = '_' + key
            try:
                self.h5_fobj.attrs[key] = value
            except Exception as e:
                warn('Could not set attribute due to error: ' + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, value)
        if not op:
            self.close()

    def construct_file_datasets(self, **kwargs):
        if len(self._datasets.intersection(self._file_attrs)) > 0:
            warn('Dataset name already exists', stacklevel=2)

        op = self.is_open
        self.open()
        for key in self._datasets:
            _key = '_' + key
            try:
                args = merge_dict(self.default_datasets_parameters, kwargs)
                self.h5_fobj.require_dataset(key, **args)
            except Exception as e:
                warn('Could not set datasets due to error: ' + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, self.h5_fobj[key])
        if not op:
            self.close()

    def get(self, item):
        if item in self._file_attrs:
            return self.get_file_attribute(item)
        elif item in self._datasets:
            return self.get_dataset(item)
        else:
            warn('No attribute or dataset ' + item, stacklevel=2)
            return None

    def get_file_attribute(self, item):
        _item = '_' + item
        op = self.is_open
        self.open()

        try:
            if item in self.h5_fobj.attrs and (super().__getattribute__(_item) is None or self.is_updating):
                setattr(self, _item, self.h5_fobj.attrs[item])
        except Exception as e:
            warn('Could not update attribute due to error: '+str(e), stacklevel=2)

        if not op:
            self.close()
        return super().__getattribute__(_item)

    def get_dataset(self, item):
        _item = '_' + item
        op = self.is_open
        self.open()

        try:
            if item in self.h5_fobj and self.is_updating:
                setattr(self, _item, self.h5_fobj[item])
        except Exception as e:
            warn('Could not update datasets due to error: ' + str(e), stacklevel=2)

        if not op:
            self.close()
        return super().__getattribute__(_item)

    def set_file_attribute(self, key, value):
        op = self.is_open
        self.open()
        _item = '_' + key

        try:
            if key not in self._file_attrs:
                self._file_attrs.update(key)
            self.h5_fobj.attrs[key] = value
        except Exception as e:
            warn('Could not set attribute due to error: ' + str(e), stacklevel=2)
        else:
            super().__setattr__(_item, value)

        if not op:
            self.close()

    def set_dataset(self, key, value=None, **kwargs):
        op = self.is_open
        self.open()
        _key = '_' + key

        try:
            if key in self._datasets:
                self.h5_fobj[key][...] = value
            else:
                self._datasets.update(key)
                args = merge_dict(self.default_datasets_parameters, kwargs)
                args['data'] = value
                self.h5_fobj.require_dataset(key, **args)
        except Exception as e:
            warn('Could not set datasets due to error: ' + str(e), stacklevel=2)
        else:
            super().__setattr__(_key, self.h5_fobj[key])

        if not op:
            self.close()

    def items(self):
        return self.items_file_attributes() + self.items_datasets()

    def items_file_attributes(self):
        result = []
        for key in self._file_attrs:
            result.append((key, self.get_file_attribute(key)))
        return result

    def items_datasets(self):
        result = []
        for key in self._datasets:
            result.append((key, self.get_dataset(key)))
        return result

    def keys(self):
        return self.keys_file_attributes() + self.keys_datasets()

    def keys_file_attributes(self):
        return list(self._file_attrs)

    def keys_datasets(self):
        return list(self._datasets)

    def pop(self, key):
        if key in self._file_attrs:
            return self.pop_file_attribute(key)
        elif key in self._datasets:
            return self.pop_dataset(key)
        else:
            warn('No attribute or dataset ' + key, stacklevel=2)
            return None

    def pop_file_attribute(self, key):
        value = self.get_file_attribute(key)
        del self.h5_fobj.attrs[key]
        return value

    def pop_dataset(self, key):
        value = self.get_dataset(key)[...]
        del self.h5_fobj[key]
        return value

    def update_file_attrs(self, **kwargs):
        if len(self._datasets.intersection(kwargs.keys())) > 0:
            warn('Dataset name already exists', stacklevel=2)
        if len(self._file_attrs.intersection(kwargs.keys())) > 0:
            warn('Attribute name already exists', stacklevel=2)

        op = self.is_open
        self.open()
        self._file_attrs.update(kwargs.keys())
        for key, value in kwargs:
            _key = '_' + key
            try:
                self.h5_fobj.attrs[key] = value
            except Exception as e:
                warn('Could not set attribute due to error: ' + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, value)
        if not op:
            self.close()

    def update_datasets(self, **kwargs):
        if len(self._file_attrs.intersection(kwargs.keys())) > 0:
            warn('Attribute name already exists', stacklevel=2)
        if len(self._datasets.intersection(kwargs.keys())) > 0:
            warn('Dataset name already exists', stacklevel=2)

        op = self.is_open
        self.open()
        self._datasets.update(kwargs.keys())
        for key, value in kwargs:
            _key = '_' + key
            try:
                args = merge_dict(self.default_datasets_parameters, value)
                self.h5_fobj.require_dataset(key, **args)
            except Exception as e:
                warn('Could not set datasets due to error: ' + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, self.h5_fobj[key])
        if not op:
            self.close()

    def open(self, mode='r+', exc=False, validate=False, **kwargs):
        if not self.is_open:
            try:
                self.h5_fobj = h5py.File(self.path.as_posix(), mode=mode)
            except Exception as e:
                if exc:
                    warn('Could not open' + self.path.as_posix() + 'due to error: ' + str(e), stacklevel=2)
                    self.is_open = False
                    self.h5_fobj = None
                    return None
                else:
                    raise e
            else:
                self.is_open = True
                if validate:
                    self.validate_file_structure(**kwargs)
                return self.h5_fobj

    def close(self):
        if self.is_open:
            self.h5_fobj.flush()
            self.h5_fobj.close()
            self.is_open = False
        return not self.is_open

    def copy(self, path=None, init=False):
        if path is None:
            new = HDF5container(path=self.path)
        else:
            new = HDF5container(path=path)
        new.is_open = self.is_open
        new.is_updating = self.is_updating
        new.cargs = self.cargs.copy()
        new.default_datasets_parameters = self.default_datasets_parameters.copy()
        new._file_attrs = self._file_attrs.copy()
        new._datasets = self._datasets.copy()
        if init:
            new.construct()
        return new

    def report_file_structure(self):
        op = self.is_open
        self.open()

        # Construct Structure Report Dictionary
        report = {'file_type': {'valid': False, 'differences': {'object': self.container_type, 'file': None}},
                  'attrs': {'valid': False, 'differences': {'object': None, 'file': None}},
                  'datasets': {'valid': False, 'differences': {'object': None, 'file': None}}}

        # Check H5 File Type
        if 'file_type' in self.h5_fobj.attrs:
            if self.h5_fobj.attrs['file_type'] == self.container_type:
                report['file_type']['valid'] = True
                report['file_type']['differences']['object'] = None
            else:
                report['file_type']['differences']['file'] = self.h5_fobj.attrs['file_type']

        # Check File Attributes
        if self.h5_fobj.attrs.keys() == self.file_attrs.keys():
            report['attrs']['valid'] = True
        else:
            f_attr_set = set(self.h5_fobj.attrs.keys())
            o_attr_set = set(self.file_attrs.keys())
            report['attrs']['differences']['object'] = o_attr_set - f_attr_set
            report['attrs']['differences']['file'] = f_attr_set - o_attr_set

        # Check File Datasets
        if self.h5_fobj.datasets.keys() == self.datasets.keys():
            report['attrs']['valid'] = True
        else:
            f_attr_set = set(self.h5_fobj.datasets.keys())
            o_attr_set = set(self.datasets.keys())
            report['datasets']['differences']['object'] = o_attr_set - f_attr_set
            report['datasets']['differences']['file'] = f_attr_set - o_attr_set

        if not op:
            self.close()
        return report

    def validate_file_structure(self, file_type=True, o_attrs=False, f_attrs=True, o_datasets=False, f_datasets=True):
        report = self.report_file_structure()
        # Validate File Type
        if file_type and not report['file_type']['valid']:
            warn(self.path.as_posix() + ' file type is not a ' + self.container_type, stacklevel=2)
        # Validate Attributes
        if not report['attrs']['valid']:
            if o_attrs and report['attrs']['differences']['object'] is not None:
                warn(self.path.as_posix() + ' is missing attributes', stacklevel=2)
            if f_attrs and report['attrs']['differences']['file'] is not None:
                warn(self.path.as_posix() + ' has extra attributes', stacklevel=2)
        # Validate Datasets
        if not report['datasets']['valid']:
            if o_datasets and report['datasets']['differences']['object'] is not None:
                warn(self.path.as_posix() + ' is missing datasets', stacklevel=2)
            if f_datasets and report['datasets']['differences']['file'] is not None:
                warn(self.path.as_posix() + ' has extra datasets', stacklevel=2)


class HDF5linkedDataset:
    pass


class EventLogger(HDF5container):
    event_fields = bidict(Time=0, DeltaTime=1, StartTime=2, Type=3)
    event_dtype = np.dtype([("Time", np.float),
                            ("DeltaTime", np.float),
                            ("StartTime", np.float),
                            ("Type", h5py.string_dtype(encoding='utf-8'))])
    container_type = 'EventLog'

    def __init__(self, path=None, io_trigger=None, init=False):
        super().__init__(path=path)

        self.event_types = {}
        self.start_datetime = None
        self.start_time_counter = None
        if io_trigger is None:
            self.io_trigger = AudioTrigger()
        else:
            self.io_trigger = io_trigger

        if init:
            self.construct()

    def __repr__(self):
        return repr(self.start_datetime)

    def __len__(self):
        pass

    def construct(self, _open=False, **kwargs):
        super().construct(_open=False, **kwargs)
        self.update_datasets(Events={"shape": (0, len(self.event_dtype)), "dtype": self.event_dtype,
                                     "maxshape": (None, len(self.event_dtype))})

    def set_time(self):
        self.start_datetime = datetime.datetime.now()
        self.start_time_counter = time.perf_counter()
        self.append({'Time': self.start_datetime, 'DeltaTime': 0, 'Type': 'TimeSet'})

    def create_event(self,  _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {'Time': now, 'DeltaTime': seconds, 'Type': _type, **kwargs}

    def append(self, _type, **kwargs):
        if isinstance(_type, dict):
            super().append(_type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            super().append(event)

    def h5link(self):
        pass

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


class SubjectEventLogger(EventLogger):
    def __init__(self):
        self.file_attrs.update(subject='Subject')
        self.datasets.update()


# Functions #
def merge_dict(dict1, dict2, copy=True):
    if dict2 is not None:
        if copy:
            dict1 = dict1.copy()
        for key, value in dict2.items():
            dict1[key] = value
    return dict1
