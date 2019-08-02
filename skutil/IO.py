import pandas as pd
import threading

class DatasetReader(object):
    def __init__(self, train_path, test_path=None, val_path=None, reserve=True):
        pass

    def __new__(cls, train_path, test_path=None, val_path=None, reserve=True):
        if not reserve:
            return object.__new__(cls)
        else:
            pass
