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
import pathlib
import datetime
import collections.abc

# Downloaded Libraries #
import h5py
import numpy as np

########## Definitions ##########

# Classes #

class HDF5container:
    file_attr = {'type': 'Type'}
    datasets = {}

    def __init__(self, path=None, init=False):
        self._path = None
        self.path = path
        self.is_open = False
        self.cargs = {'compression': 'gzip', 'compression_opts': 4}

        self.h5_fobj = None
        self.is_updating = False

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

    def __repr__(self):
        return repr((self.start))

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
        self.__dict__.is_updating(state)

    def __len__(self):
        return self.n_samples

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


class EventLogger(HDF5container):
    file_attr = {'type': 'Type', 'subject': 'Subject'}
    datasets = {'events', 'Events'}

    def __init__(self, name, subject=None, path=None, init=False):
        super().__init__(path=path, init=init)

        self._type = 'EventLog'
        self._subject = subject
        
