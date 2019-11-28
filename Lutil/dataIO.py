import csv
import datetime
import logging
import operator
import os
import re
import threading
import warnings

import chardet
import numpy as np
import pandas as pd
from Lutil._exceptions import DuplicateSettingWarning, SpeculationFailedError
from pandas.api.types import is_numeric_dtype, is_string_dtype

__all__ = ["DataReader", "AutoSaver"]


class DataReader(object):
    _instances = {}
    _instances_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if "_id" not in kwargs:
            _id = 0
        else:
            _id = kwargs["_id"]

        with DataReader._instances_lock:
            if _id in DataReader._instances:
                return DataReader._instances[_id]
            else:
                new_instance = object.__new__(cls)
                DataReader._instances[_id] = new_instance
                return new_instance

    def __init__(self, train_path=None, test_path=None, val_path=None, _id="default", read_func=None, **read_kwargs):
        assert read_func is None or callable(read_func)
        if hasattr(self, "_id"):
            self.__init_existed__(train_path=train_path, test_path=test_path,
                                  val_path=val_path, _id=_id, read_func=read_func, **read_kwargs)
        else:
            self.__init_new__(train_path=train_path, test_path=test_path,
                              val_path=val_path, _id=_id, read_func=read_func, **read_kwargs)

    def __init_existed__(self, train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_kwargs):
        assert(_id == self._id)
        if train_path is not None:
            self.train_path = train_path
        if test_path is not None:
            self.test_path = test_path
        if val_path is not None:
            self.val_path = val_path

        if read_kwargs:
            if operator.eq(read_kwargs, self.__read_kwargs):
                logging.info(
                    f"Data reading configuration is already set for {self.__class__} object, it's unnecessary to set it again.")
            else:
                raise ValueError(
                    "Newly set data reading configuration is different from the cached value. If you do want this, please specify '_id=N' as a parameter.")

        if read_func:
            if read_func is self.__read_func:
                logging.info(
                    f"Data reading function is already set for {self.__class__} object, it's unnecessary to set it again.")
            else:
                raise ValueError(
                    "Newly set data reading function is different from the cached value. If you do want this, please specify '_id=N' as a parameter.")

    def __init_new__(self, train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_kwargs):
        try:
            if train_path is not None:
                assert os.path.exists(train_path)
            if test_path is not None:
                assert os.path.exists(test_path)
            if val_path is not None:
                assert os.path.exists(val_path)
        except Exception as e:
            raise ValueError("Some path is invalid or does not exist.", e)

        self._id = _id
        self.__read_kwargs = read_kwargs
        self.__read_func = read_func

        if self.__read_func is None:
            self.__read_func = pd.read_csv

        if train_path:
            self._train_path = train_path
        if test_path:
            self._test_path = test_path
        if val_path:
            self._val_path = val_path

    @property
    def train_path(self):
        if hasattr(self, "_train_path"):
            return self._train_path
        else:
            raise AttributeError(
                f"'{self.__class__}' object has no attribute 'train_path'.")

    @train_path.setter
    def train_path(self, value):
        if hasattr(self, "_train_path"):
            if self.train_path == value:
                logging.info(
                    f"'train_path' of {self.__class__} object is already set as {value}, it's unnecessary to set it again.")
            else:
                raise ValueError(
                    "Newly set train_path is different from the cached value. If you do want this, please specify '_id=N' as a parameter.")
        else:
            warnings.warn(DuplicateSettingWarning("train", self))
            self._train_path = value

    @property
    def test_path(self):
        if hasattr(self, "_test_path"):
            return self._test_path
        else:
            raise AttributeError(
                f"'{self.__class__}' object has no attribute 'test_path'.")

    @test_path.setter
    def test_path(self, value):
        if hasattr(self, "_test_path"):
            if self.test_path == value:
                logging.info(
                    f"'test_path' of {self.__class__} object is already set as {value}, it's unnecessary to set it again.")
            else:
                raise ValueError(
                    "Newly set test_path is different from the cached value. If you do want this, please specify '_id=N' as a parameter.")
        else:
            warnings.warn(DuplicateSettingWarning("test", self))
            self._test_path = value

    @property
    def val_path(self):
        if hasattr(self, "_val_path"):
            return self._val_path
        else:
            raise AttributeError(
                f"'{self.__class__}' object has no attribute 'val_path'.")

    @val_path.setter
    def val_path(self, value):
        if hasattr(self, "_val_path"):
            if self.val_path == value:
                logging.info(
                    f"'val_path' of {self.__class__} object is already set as {value}, it's unnecessary to set it again.")
            else:
                raise ValueError(
                    "Newly set val_path is different from the cached value. If you do want this, please specify '_id=N' as a parameter.")
        else:
            warnings.warn(DuplicateSettingWarning("val", self))
            self._val_path = value

    def train(self):
        return self.__read_func(self.train_path, **self.__read_kwargs)

    def test(self):
        return self.__read_func(self.test_path, **self.__read_kwargs)

    def val(self):
        return self.__read_func(self.val_path, **self.__read_kwargs)


class AutoSaver(object):
    def __init__(self, save_dir="", example_path=None, **default_kwargs):
        if example_path and default_kwargs:
            raise ValueError(
                "You cannot set both 'example_path' and give other saving kwargs at the same time.")

        if save_dir and not os.path.exists(save_dir):
            os.mkdir(save_dir)

        self.save_dir = save_dir
        self.example_path = example_path
        self.default_kwargs = default_kwargs

    def __save_by_to_csv(self, X, filename):
        if self.example_path and self.__used_kwargs:
            raise ValueError(
                "You cannot set both 'example_path' and give other saving kwargs at the same time.")

        if self.example_path:
            return self.__save_by_to_csv_speculating(X, filename)
        else:
            if not isinstance(X, (pd.DataFrame, pd.Series)):
                raise TypeError(
                    f"'X' must be a pd.DataFrame or pd.Series, rather than {X.__class__} if you do not provide an example csv file, or are using self-defined keyword parameters.")
            return X.to_csv(os.path.join(self.save_dir, filename), **self.__used_kwargs)

    def __speculate_ordered_index(self, s):
        s = s.copy()
        if is_string_dtype(s):
            return (True, s.iloc[0])

        step = len(s)//100 + 1

        for i in range(0, len(s)-1, step):
            if s.iloc[i+step] - s.iloc[i] != step:
                return (False,)
        return True, s.iloc[0]

    def __try_add_column(self, X):
        e = SpeculationFailedError(
            "The number of columns of 'X' is smaller than that in the example file.")
        col_ix = self.__example_df.shape[1] - X.shape[1] - 1
        example_spec = self.__speculate_ordered_index(
            self.__example_df.iloc[:, col_ix])
        X = X.reset_index(level=0)
        if example_spec[0]:
            try:
                X.iloc[:, 0] = X.iloc[:, 0].astype(int)
            except:
                pass
            X_spec = self.__speculate_ordered_index(X.iloc[:, 0])
            if X_spec[0] and X_spec[1] == example_spec[1]:
                pass  # Index addition OK
            else:
                if example_spec[1] == 0:
                    X.iloc[:, 0] = np.arange(X.shape[0])
                elif example_spec[1] == 1:
                    X.iloc[:, 0] = np.arange(1, X.shape[0]+1)
                else:
                    raise e
        elif X.shape[0] == self.__example_df.shape[0]:
            X.iloc[:, 0] = self.__example_df.iloc[:, 0]
        else:
            raise e

        return X

    def __get_example_df(self):
        with open(self.example_path, "rb") as f:
            buffer = f.read()
            enc = chardet.detect(buffer)["encoding"]

        with open(self.example_path, "r", encoding=enc) as f:
            df = pd.read_csv(f, header=None, nrows=1)

        has_header = is_string_dtype(df.iloc[0, :])

        with open(self.example_path, "r", encoding=enc) as f:
            sniffer = csv.Sniffer()
            content = f.read()
            try:
                dialect = sniffer.sniff(content)
                has_header = sniffer.has_header(content) or has_header

            except Exception:
                fixed_content = "\n".join(
                    line+"," for line in content.split("\n"))
                dialect = sniffer.sniff(fixed_content)
                has_header = sniffer.has_header(fixed_content) or has_header

            dialect_kwargs = {
                "sep": dialect.delimiter,
                "line_terminator": dialect.lineterminator,
                "doublequote": dialect.doublequote,
                "quotechar": dialect.quotechar,
                "escapechar": dialect.escapechar,
                "quoting": dialect.quoting
            }

            f.seek(0, 0)
            example_df = pd.read_csv(
                f, dialect=dialect, index_col=False, header=0 if has_header else None)
        self.__example_df = example_df
        self.__has_header = has_header
        self.__dialect_kwargs = dialect_kwargs

    def __save_by_to_csv_speculating(self, X, filename):
        if not isinstance(X, (pd.DataFrame, pd.Series, np.ndarray)):
            raise TypeError(
                f"'X' must be either a pd.DataFrame, pd.Series or np.ndarray, rather than {X.__class__} if you provide an example csv file.")

        X = pd.DataFrame(X)
        self.__get_example_df()

        while X.shape[1] > self.__example_df.shape[1]:
            # Drop columns of X
            if self.__speculate_ordered_index(X.iloc[:, 0])[0]:
                X = X.drop(columns=[X.columns.values[0]])
            else:
                raise SpeculationFailedError(
                    "The number of columns of 'X' is larger than that in the example file.")

        while X.shape[1] < self.__example_df.shape[1]:
            X = self.__try_add_column(X)

        for i in range(X.shape[1]):
            if self.__speculate_ordered_index(X.iloc[:, i])[0] and is_numeric_dtype(X.iloc[:, i]):
                X.iloc[:, i] = X.iloc[:, i].astype(int)
            else:
                break

        example_spec_res = self.__speculate_ordered_index(
            self.__example_df.iloc[:, 0])
        if example_spec_res[0] and is_numeric_dtype(example_spec_res[1]):
            X.iloc[:, 0] = np.arange(
                example_spec_res[1], example_spec_res[1]+X.shape[0])

        fullpath = os.path.join(self.save_dir, filename)

        if self.__has_header:
            header = [re.compile(r"Unnamed: \d+").sub("", i)
                      for i in self.__example_df.columns.values]
            return X.to_csv(fullpath, header=header, index=False, **self.__dialect_kwargs)
        else:
            return X.to_csv(fullpath, header=False, index=False, **self.__dialect_kwargs)

    def save(self, X, filename=None, memo=None, **kwargs):
        if not filename:
            filename = datetime.datetime.now().strftime(r"%m%d-%H%M%S") + ".csv"
        self.__used_kwargs = {**self.default_kwargs, **kwargs}

        res = self.__save_by_to_csv(X, filename)

        if memo:
            with open(os.path.join(self.save_dir, "memo.txt"), "a+", encoding="utf-8") as f:
                f.write(f"{filename}: {str(memo)}" + "\n")

        return res
