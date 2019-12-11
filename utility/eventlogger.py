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
import collections
import copy
import csv
import datetime
import pathlib
import time
import uuid
from warnings import warn


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
        self.append({"Time": self.start_datetime, "DeltaTime": 0, "Type": "TimeSet"})

    def create_event(self, _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {"Time": now, "DeltaTime": seconds, "Type": _type, **kwargs}

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
        self.append(_type="Trigger", **kwargs)

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
            result.append(key + ": " + str(value))
        return result


class HDF5container(object):
    CONTAINER_TYPE = "Abstract"
    VERSION = "0.0.0"

    # Instantiation/Destruction
    def __init__(self, path=None, init=False):
        self._path = None
        self._file_attrs = {"FileType", "Version"}
        self._datasets = set()

        self.path = path
        self.is_open = False
        self.is_updating = False
        self.cargs = {"compression": "gzip", "compression_opts": 4}
        self.default_datasets_parameters = self.cargs.copy()

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

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo={}):
        new = self.deepcopy(init=True, memo=memo)
        return new

    def __del__(self):
        self.close()

    # Pickling
    def __getstate__(self):
        state = self.__dict__.copy()
        name = state["path"].as_posix()
        open_state = state["is_open"]
        if self.is_open:
            fobj = state["h5_fobj"]
            fobj.flush()
            fobj.close()
        state["h5_fobj"] = (name, open_state)
        return state

    def __setstate__(self, state):
        name, open_state = state["h5_fobj"]
        state["h5_fobj"] = h5py.File(name.as_posix(), "r+")
        if not open_state:
            state["h5_fobj"].close()
        self.__dict__.update(state)

    # Attribute Access
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

    # Container Magic Methods
    def __len__(self):
        op = self.is_open
        self.open()
        length = len(self.h5_fobj)
        if not op:
            self.close()
        return length

    def __getitem__(self, item):
        if item in self._datasets:
            data = self.get_dataset(item)
        else:
            raise KeyError(item)
        return data

    def __setitem__(self, key, value):
        self.set_dataset(key, value)

    # Context Managers
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    # Constructors
    def construct(self, open_=False, **kwargs):
        if self.path.is_file():
            self.open(validate=True, )**kwargs
            if not open_:
                self.close()
        else:
            self.construct_file(open_=open_)

    def construct_file(self, open_=False):
        self.open()
        self.construct_file_attributes()
        self.construct_file_datasets()
        if open_:
            return self.h5_fobj
        else:
            self.close()
            return None

    def construct_file_attributes(self, value=None):
        if len(self._file_attrs.intersection(self._datasets)) > 0:
            warn("Attribute name already exists", stacklevel=2)

        op = self.is_open
        self.open()
        for key in self._file_attrs:
            _key = "_" + key
            try:
                self.h5_fobj.attrs[key] = value
            except Exception as e:
                warn("Could not set attribute due to error: " + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, value)
        if not op:
            self.close()

    def construct_file_datasets(self, **kwargs):
        if len(self._datasets.intersection(self._file_attrs)) > 0:
            warn("Dataset name already exists", stacklevel=2)

        op = self.is_open
        self.open()
        for key in self._datasets:
            _key = "_" + key
            try:
                args = merge_dict(self.default_datasets_parameters, kwargs)
                self.h5_fobj.require_dataset(key, **args)
            except Exception as e:
                warn("Could not set datasets due to error: " + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, self.h5_fobj[key])
        if not op:
            self.close()

    # Copy Methods
    def copy(self):
        return self.__copy__()

    def deepcopy(self, path=None, init=False, memo={}):
        if path is None:
            new = type(self)(path=self.path.as_posix)
        else:
            new = type(self)(path=path)
        new._file_attrs = copy.deepcopy(self._file_attrs, memo=memo)
        new._datasets = copy.deepcopy(self._datasets, memo=memo)
        new.is_open = self.is_open
        new.is_updating = self.is_updating
        new.cargs = copy.deepcopy(self.cargs, memo=memo)
        new.default_datasets_parameters = copy.deepcopy(self.cargs, memo=memo)

        if init:
            new.construct()
        return new

    # Getter and Setters
    def get(self, item):
        if item in self._file_attrs:
            return self.get_file_attribute(item)
        elif item in self._datasets:
            return self.get_dataset(item)
        else:
            warn("No attribute or dataset " + item, stacklevel=2)
            return None

    def get_file_attribute(self, item):
        _item = "_" + item
        op = self.is_open
        self.open()

        try:
            if item in self.h5_fobj.attrs and (super().__getattribute__(_item) is None or self.is_updating):
                setattr(self, _item, self.h5_fobj.attrs[item])
        except Exception as e:
            warn("Could not update attribute due to error: "+str(e), stacklevel=2)

        if not op:
            self.close()
        return super().__getattribute__(_item)

    def get_dataset(self, item):
        _item = "_" + item
        op = self.is_open
        self.open()

        try:
            if item in self.h5_fobj and self.is_updating:
                setattr(self, _item, self.h5_fobj[item])
        except Exception as e:
            warn("Could not update datasets due to error: " + str(e), stacklevel=2)

        if not op:
            self.close()
        return super().__getattribute__(_item)

    def set_file_attribute(self, key, value):
        op = self.is_open
        self.open()
        _item = "_" + key

        try:
            if key not in self._file_attrs:
                self._file_attrs.update(key)
            self.h5_fobj.attrs[key] = value
        except Exception as e:
            warn("Could not set attribute due to error: " + str(e), stacklevel=2)
        else:
            super().__setattr__(_item, value)

        if not op:
            self.close()

    def set_dataset(self, key, value=None, **kwargs):
        op = self.is_open
        self.open()
        _key = "_" + key

        try:
            if key in self._datasets:
                self.h5_fobj[key][...] = value
            else:
                self._datasets.update(key)
                args = merge_dict(self.default_datasets_parameters, kwargs)
                args["data"] = value
                self.h5_fobj.require_dataset(key, **args)
        except Exception as e:
            warn("Could not set datasets due to error: " + str(e), stacklevel=2)
        else:
            super().__setattr__(_key, self.h5_fobj[key])

        if not op:
            self.close()

    #  Mapping Items Methods
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

    # Mapping Keys Methods
    def keys(self):
        return self.keys_file_attributes() + self.keys_datasets()

    def keys_file_attributes(self):
        return list(self._file_attrs)

    def keys_datasets(self):
        return list(self._datasets)

    # Mapping Pop Methods
    def pop(self, key):
        if key in self._file_attrs:
            return self.pop_file_attribute(key)
        elif key in self._datasets:
            return self.pop_dataset(key)
        else:
            warn("No attribute or dataset " + key, stacklevel=2)
            return None

    def pop_file_attribute(self, key):
        value = self.get_file_attribute(key)
        del self.h5_fobj.attrs[key]
        return value

    def pop_dataset(self, key):
        value = self.get_dataset(key)[...]
        del self.h5_fobj[key]
        return value

    # Mapping Update Methods
    def update_file_attrs(self, **kwargs):
        if len(self._datasets.intersection(kwargs.keys())) > 0:
            warn("Dataset name already exists", stacklevel=2)
        if len(self._file_attrs.intersection(kwargs.keys())) > 0:
            warn("Attribute name already exists", stacklevel=2)

        op = self.is_open
        self.open()
        self._file_attrs.update(kwargs.keys())
        for key, value in kwargs:
            _key = "_" + key
            try:
                self.h5_fobj.attrs[key] = value
            except Exception as e:
                warn("Could not set attribute due to error: " + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, value)
        if not op:
            self.close()

    def update_datasets(self, **kwargs):
        if len(self._file_attrs.intersection(kwargs.keys())) > 0:
            warn("Attribute name already exists", stacklevel=2)
        if len(self._datasets.intersection(kwargs.keys())) > 0:
            warn("Dataset name already exists", stacklevel=2)

        op = self.is_open
        self.open()
        self._datasets.update(kwargs.keys())
        for key, value in kwargs:
            _key = "_" + key
            try:
                args = merge_dict(self.default_datasets_parameters, value)
                self.h5_fobj.require_dataset(key, **args)
            except Exception as e:
                warn("Could not set datasets due to error: " + str(e), stacklevel=2)
            else:
                super().__setattr__(_key, self.h5_fobj[key])
        if not op:
            self.close()

    # File Methods
    def open(self, mode="r+", exc=False, validate=False, **kwargs):
        if not self.is_open:
            try:
                self.h5_fobj = h5py.File(self.path.as_posix(), mode=mode)
            except Exception as e:
                if exc:
                    warn("Could not open" + self.path.as_posix() + "due to error: " + str(e), stacklevel=2)
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

    # General Methods
    def append2dataset(self, name, data, axis=0):
        dataset = self.get_dataset(name)
        s_shape = dataset.shape
        d_shape = data.shape
        f_shape = list(s_shape)
        f_shape[axis] = s_shape[axis] + d_shape[axis]
        slicing = tuple(slice(s_shape[ax]) for ax in range(0, axis)) + (-d_shape[axis], ...)

        dataset.resize(*f_shape)
        dataset[slicing] = data

    def report_file_structure(self):
        op = self.is_open
        self.open()

        # Construct Structure Report Dictionary
        report = {"file_type": {"valid": False, "differences": {"object": self.CONTAINER_TYPE, "file": None}},
                  "attrs": {"valid": False, "differences": {"object": None, "file": None}},
                  "datasets": {"valid": False, "differences": {"object": None, "file": None}}}

        # Check H5 File Type
        if "file_type" in self.h5_fobj.attrs:
            if self.h5_fobj.attrs["file_type"] == self.CONTAINER_TYPE:
                report["file_type"]["valid"] = True
                report["file_type"]["differences"]["object"] = None
            else:
                report["file_type"]["differences"]["file"] = self.h5_fobj.attrs["file_type"]

        # Check File Attributes
        if self.h5_fobj.attrs.keys() == self.file_attrs.keys():
            report["attrs"]["valid"] = True
        else:
            f_attr_set = set(self.h5_fobj.attrs.keys())
            o_attr_set = set(self.file_attrs.keys())
            report["attrs"]["differences"]["object"] = o_attr_set - f_attr_set
            report["attrs"]["differences"]["file"] = f_attr_set - o_attr_set

        # Check File Datasets
        if self.h5_fobj.datasets.keys() == self.datasets.keys():
            report["attrs"]["valid"] = True
        else:
            f_attr_set = set(self.h5_fobj.datasets.keys())
            o_attr_set = set(self.datasets.keys())
            report["datasets"]["differences"]["object"] = o_attr_set - f_attr_set
            report["datasets"]["differences"]["file"] = f_attr_set - o_attr_set

        if not op:
            self.close()
        return report

    def validate_file_structure(self, file_type=True, o_attrs=False, f_attrs=True, o_datasets=False, f_datasets=True):
        report = self.report_file_structure()
        # Validate File Type
        if file_type and not report["file_type"]["valid"]:
            warn(self.path.as_posix() + " file type is not a " + self.CONTAINER_TYPE, stacklevel=2)
        # Validate Attributes
        if not report["attrs"]["valid"]:
            if o_attrs and report["attrs"]["differences"]["object"] is not None:
                warn(self.path.as_posix() + " is missing attributes", stacklevel=2)
            if f_attrs and report["attrs"]["differences"]["file"] is not None:
                warn(self.path.as_posix() + " has extra attributes", stacklevel=2)
        # Validate Datasets
        if not report["datasets"]["valid"]:
            if o_datasets and report["datasets"]["differences"]["object"] is not None:
                warn(self.path.as_posix() + " is missing datasets", stacklevel=2)
            if f_datasets and report["datasets"]["differences"]["file"] is not None:
                warn(self.path.as_posix() + " has extra datasets", stacklevel=2)


class HDF5references(object):
    def __init__(self, dataset, reference_field="", dtype=None, init=True):
        self._dataset = None

        self.reference_field = ""
        self.dtype = None
        self.fields = bidict()
        self.references = bidict()

        self._reference_array = None

        if init:
            self.construct(dataset, reference_field, dtype)

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    @property
    def reference_array(self):
        try:
            self._reference_array = self._dataset[self.reference_field]
        except Exception as e:
            warn(e)
        finally:
            return self._reference_array

    # Container Magic Methods
    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = (items,)
        
        result = []
        for item in items:
            if isinstance(item, uuid.UUID):
                result.append(self.get_index(item))
            elif isinstance(item, tuple):
                result.append(self.get_id(item))
        return tuple(result)

    # Generic Methods #
    # Constructors Methods
    def construct(self, dataset, reference_field, dtype=None):
        self._dataset = dataset

        if dtype is None:
            self.dtype = self._dataset.dtype
        else:
            self.dtype = dtype

        for i, field in enumerate(self.dtype.descr):
            self.fields[field] = i

        if reference_field in self.fields:
            self.reference_field = reference_field
        else:
            raise NameError

        self._reference_array = self._dataset[self.reference_field]

    # Copy Methods
    def copy(self):
        return self.__copy__()

    # Getter and Setters
    def new_reference(self, index=None, axis=0, id_=None):
        if index is None:
            index = self._dataset.shape
            index[axis] = index[axis] + 1
        if id_ is None:
            id_ = uuid.uuid4()
        self.set_reference(id_, index)
        return id_

    def set_reference(self, index, id_):
        item = self._dataset[index]
        item[self.reference_field] = id_
        self._dataset[index] = item
        self.references[id_] = index

    def get_index(self, id_):
        try:
            index = self.find_index(id_)
            if index:
                self.references[id_] = index
            else:
                raise KeyError
        except Exception as e:
            warn(e)
        finally:
            return self.references[id_]

    def find_index(self, id_):
        indices = np.where(self.reference_array == id_)
        if len(indices) == 0:
            index = None
        elif len(indices[0]) > 1:
            raise KeyError
        else:
            temp = []
            for axis in indices:
                temp.append(axis[0])
            index = tuple(temp)
        return index

    def get_id(self, index):
        try:
            self.references.inverse[index] = self.find_id(index)
        except Exception as e:
            warn(e)
        finally:
            return self.references.inverse[index]

    def find_id(self, index):
        return self.reference_array[index]


class HDF5linkedDatasets(object):
    def __init__(self):
        self.references = {}

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    # Container Magic Methods
    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = (items,)

        result = []
        for item in items:
            if isinstance(item, uuid.UUID):
                result.append(self.get_indices(item))
            elif isinstance(item, str):
                result.append(self.references[item])
        return result

    # Copy Methods
    def copy(self):
        return self.__copy__()

    def add_datset(self, name, dataset, link_name):
        self.references[name] = HDF5references(dataset, link_name)

    def pop_dataset(self, name):
        return self.references.pop(name)

    def new_link(self, locations=None, axis=0, id_=None):
        if id_ is None:
            id_ = uuid.uuid4()

        if not locations:
            for references in self.references.values():
                references.new_reference(axis=axis, id_=id_)
        else:
            for name, index in locations.items():
                self.references[name].new_reference(index, id_)

    def get_index(self, name, id_):
        return self.references[name][id_]

    def get_indices(self, id_, datasets=None):
        result = {}
        if not datasets:
            for name, references in self.references.items():
                result[name] = references[id_]
        else:
            if isinstance(datasets, str):
                datasets = (datasets,)
            for name in datasets:
                result[name] = self.references[name][id_]

    def get_id(self, name, index):
        return self.references[name][index]

    def get_linked_index(self, source, index, datasets=None):
        id_ = self.get_id(source, index)
        return self.get_indices(id_, datasets)


class HDF5hierarchicalDatasets(object):
    def __init__(self, h5_container=None):
        self.h5_container = None

        self.parent_name = ""
        self.parent_dataset = None
        self.child_datasets = bidict()
        self.dataset_links = HDF5linkedDatasets()

        self.child_name_field = ""

    def __getitem__(self, item):
        pass

    def construct(self):
        pass

    def create_parent_dataset(self, name, link_name, **kwargs):
        self.dataset_links.pop_dataset(self.parent_name)
        self.parent_name = name
        self.parent_dataset = self.h5_container.set_dataset(name=name, **kwargs)
        self.dataset_links.add_datset(name, self.parent_dataset, link_name)

    def set_parent_dataset(self, name, dataset, link_name):
        self.dataset_links.pop_dataset(self.parent_name)
        self.parent_name = name
        self.parent_dataset = dataset
        self.dataset_links.add_datset(name, self.parent_dataset, link_name)

    def remove_parent_dataset(self):
        self.dataset_links.pop_dataset(self.parent_name)
        self.parent_name = ""

    def create_child_dataset(self, name, link_name, **kwargs):
        dataset = self.h5_container.set_dataset(name=name, **kwargs)
        self.dataset_links.add_datset(name, dataset, link_name)

    def add_child_dataset(self, name, dataset, link_name):
        self.dataset_links.add_datset(name, dataset, link_name)

    def remove_child_dataset(self, name):
        self.dataset_links.pop_dataset(name)

    def get_item(self, index, name=None):
        if name is None:
            name = self.parent_name
            parent = self.dataset_links[name][0]
            child_name = parent[self.child_name_field]
            child = self.dataset_links.get_linked_index(name, index, datasets=child_name)[child_name]
        else:
            child = self.dataset_links[name][0]
            parent = self.dataset_links.get_linked_index(name, index, datasets=self.parent_name)[self.parent_name]

        result = list(parent) + list(child)

        return result


class HDF5linkDataset(object):
    def __init__(self, container=None, ref_name="", ref_fields=None, ref_dtype=None, ref_id=None, ref_index=None,
                 name="Type", fields=None, dtype=None, id_=None, index_name="Index"):
        self.ref_name = ref_name
        self.ref_dtype = ref_dtype
        self.ref_fields = bidict()
        self.ref_id_name = ""
        self.ref_id = ref_id
        self.ref_index = ref_index
        self._ref_data = None
        self._ref_dict = {}

        self.reference_name = name
        self.reference_name_include = True
        self.reference_dtype = dtype
        self.reference_fields = bidict()
        self.reference_id_name = ""
        self.reference_id = id_
        self.reference_index_name = index_name
        self.reference_index_include = False
        self.reference_index = 0
        self._reference_data = None
        self._reference_dict = {}

        self.h5_container = container
        self.ref_dataset = None
        self.reference_dataset = None

    def __getitem__(self, item):
        pass

    def construct(self):
        pass

    def ref_construct(self, ref_name, index=None):
        self.ref_name = ref_name
        self.ref_dtype = self.h5_container[ref_name].dtype
        for i, field in enumerate(self.ref_dtype.descr):
            self.ref_fields[field] = i
        self.ref_index = index

    def data_construct(self, name, index=None):
        self.reference_name = name
        self.reference_dtype = self.h5_container[name].dtype
        for i, field in enumerate(self.reference_dtype.descr):
            self.reference_fields[field] = i
        self.reference_index = index

    def get_reference(self):
        axis = self.ref_index_axis
        shape = self.ref_dataset.shape
        slicing = tuple(slice(shape[ax]) for ax in range(0, axis)) + (-self.ref_index, ...)
        self._ref_data = self.ref_dataset[slicing]
        self._ref_dict.clear()
        return

    def set_reference(self, name=None, fields=None, dtype=None, index=None, axis=None):
        if name: self.ref_name = name
        if axis: self.ref_index_axis = axis
        if index: self.ref_index = index
        self.ref_dataset = self.h5_container[self.ref_name]

        if dtype:
            self.ref_dtype = dtype
        else:
            self.ref_dtype = self.ref_dataset.dtype

        if fields:
            self.ref_fields = fields
        else:
            for i, field in enumerate(self.ref_dtype.descr):
                self.ref_fields[field] = i

    def set_referenceed(self, ):
        pass

    def get_item(self, key, axis=None):
        if key in self.ref_fields:
            return self.get_ref_item(key, axis)
        elif key in self.reference_fields:
            return self.get_reference_item(key, axis)
        else:
            raise KeyError

    def get_ref_item(self, key):
        self.get_reference()



    def get_reference_item(self, key):
        pass

    def set_item(self, key, value, ref=False):
        pass

    def set_ref_item(self, key, value):
        pass

    def set_reference_item(self, key, value):
        pass

    @staticmethod
    def dataset_find(dataset, value, axis):
        if isinstance(axis, str):
            return np.where(dataset[axis] == value)
        else:
            pass




class EventLogger(HDF5container):
    CONTAINER_TYPE = "EventLog"
    EVENT_FIELDS = bidict(Time=0, DeltaTime=1, StartTime=2, Type=3)
    EVENT_DTYPE = np.dtype([("Time", np.float),
                            ("DeltaTime", np.float),
                            ("StartTime", np.float),
                            ("Type", h5py.string_dtype(encoding="utf-8"))])

    # Instantiation/Destruction
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

    # Container Magic Methods
    def __len__(self):
        return self.Events.len()

    def __getitem__(self, item):
        if isinstance(item, str):
            return super().__getitem__(item)
        else:
            return self.re

    # Representations
    def __repr__(self):
        return repr(self.start_datetime)

    # Constructors
    def construct(self, _open=False, **kwargs):
        super().construct(_open=False, **kwargs)
        self.create_event_dataset(name="Events", dtype=self.EVENT_DTYPE)

    # Sequence Methods
    def append(self, _type, **kwargs):
        if isinstance(_type, dict):
            self.append_event(_type)
        else:
            event = self.create_event(_type=_type, **kwargs)
            self.append_event(event)

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

    # User Event Methods
    def set_time(self):
        self.start_datetime = datetime.datetime.now()
        self.start_time_counter = time.perf_counter()
        self.append({"Time": self.start_datetime, "DeltaTime": 0, "StartTime": self.start_datetime, "Type": "TimeSet"})

    def create_event(self,  _type, **kwargs):
        seconds = round(time.perf_counter() - self.start_time_counter, 6)
        now = self.start_datetime + datetime.timedelta(seconds=seconds)
        return {"Time": now, "DeltaTime": seconds, "StartTime": self.start_datetime, "Type": _type, **kwargs}

    def create_event_dataset(self, name, dtype, data=None):
        if data is not None:
            m = data
        else:
            m = 0
        n_types = len(dtype)
        self.update_datasets(**{name: {"data": data, "shape": (m, n_types), "dtype": dtype, "maxshape": (None, n_types)}})

    def append_event(self, event, axis=0):
        event = event.copy()
        type_event = {field: event.pop(field) for field in self.EVENT_FIELDS}
        type_ = type_event["Type"]

        self.append_named_event(type_, event, axis)
        event_index = self[type_].shape[axis]

        self.append_type_event(type_event, event_index, axis)

    def append_named_event(self, name, event, axis=0):
        # Add Event Type
        if name not in self.event_types:
            fields = bidict(enumerate(event.keys())).inverse
            dtype = self.event2dtype(event)
            self.event_types[name] = {"fields": fields, "dtype": dtype}
            self.create_event_dataset(name, dtype)
        else:
            fields = self.event_types[name]["fields"]
            dtype = self.event_types[name]["dtype"]

        # Event Array
        event_array = self.dict2numpy(event, fields, dtype)
        self.append2dataset(name, event_array, axis)

    def append_type_event(self, event, index, axis=0):
        # Event Type Array
        event_fields = bidict(index=index, **self.EVENT_FIELDS)
        event_dtype = np.dtype(self.EVENT_DTYPE.descr.copy() + [("Index", np.int)])
        t_event_array = self.dict2numpy(event, event_fields, event_dtype)
        self.append2dataset("Event", t_event_array, axis=0)

    # Trigger Methods
    def trigger(self):
        self.io_trigger.trigger()

    def trigger_event(self, **kwargs):
        self.trigger()
        self.append(_type="Trigger", **kwargs)

    # Static Methods
    @staticmethod
    def dict2numpy(dict_, fields, dtype, pop=False):
        data = [None] * len(fields)
        for key, index in fields.items():
            if isinstance(dict_[key], datetime.datetime):
                data[index] = dict_[key].timestamp()
            else:
                data[index] = dict_[key]
            if pop:
                del dict_[key]
        return np.array(data, dtype=dtype)

    @staticmethod
    def event2dtype(event):
        dtypes = []
        for key, value in event.items():
            if isinstance(value, int):
                dtype = np.int
            elif isinstance(value, float):
                dtype = np.float
            elif isinstance(value, datetime.datetime):
                dtype = np.float
            else:
                dtype = h5py.string_dtype(encoding="utf-8")

            dtypes.append((key, dtype))
        return dtypes


class SubjectEventLogger(EventLogger):
    def __init__(self):
        self.file_attrs.update(subject="Subject")
        self.datasets.update()


# Functions #
def merge_dict(dict1, dict2, copy=True):
    if dict2 is not None:
        if copy:
            dict1 = dict1.copy()
        for key, value in dict2.items():
            dict1[key] = value
    return dict1

def np_to_dict(array):
    pass
