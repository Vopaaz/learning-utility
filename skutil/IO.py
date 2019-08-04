import pandas as pd
import threading
import logging
import os
import operator


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

    def __init__(self, train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_config):
        assert read_func is None or callable(read_func)
        if hasattr(self, "_id"):
            self.__init_existed__(train_path=train_path, test_path=test_path,
                                  val_path=val_path, _id=_id, read_func=read_func, **read_config)
        else:
            self.__init_new__(train_path=train_path, test_path=test_path,
                              val_path=val_path, _id=_id, read_func=read_func, **read_config)

    def __init_existed__(self, train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_config):
        assert(_id == self._id)
        if train_path is not None:
            self.train_path = train_path
        if test_path is not None:
            self.test_path = test_path
        if val_path is not None:
            self.val_path = val_path

        if read_config:
            if operator.eq(read_config, self.__read_config):
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

    def __init_new__(self, train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_config):
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
        self.__read_config = read_config
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
            logging.warning(
                f"A train path is set after the first initialization of {self.__class__}.")
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
            logging.warning(
                f"A test path is set after the first initialization of {self.__class__}.")
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
            logging.warning(
                f"A val path is set after the first initialization of {self.__class__}.")
            self._val_path = value

    @property
    def train(self):
        return self.__read_func(self.train_path, **self.__read_config)


    @train.setter
    def train(self):
        raise ValueError(
            f"Attibute 'train' of {self.__class_} object is read only.")

    @property
    def test(self):
        return self.__read_func(self.test_path, **self.__read_config)

    @test.setter
    def test(self):
        raise ValueError(
            f"Attibute 'test' of {self.__class_} object is read only.")

    @property
    def val(self):
        return self.__read_func(self.val_path, **self.__read_config)

    @val.setter
    def val(self):
        raise ValueError(
            f"Attibute 'val' of {self.__class_} object is read only.")


class ResultSaver(object):
    def __init__(self):
        pass

    def save(X, memo=None):
        pass