import inspect
import re
import os
import logging
import pandas as pd
import hashlib
import joblib
import numpy as np
from collections import OrderedDict


def _get_file_info(obj):
    filename = inspect.getfile(obj)
    ipython_filename_pattern = r"<ipython-input-\d+-(.{12})>"
    ipython_result = re.compile(ipython_filename_pattern).match(filename)
    if ipython_result:
        file_info = f"ipynb-{ipython_result.group(1)}"
    else:
        file_info, _ = os.path.splitext(os.path.basename(filename))

    return file_info


def _get_name(func, applied_args, ignore=[]):
    file_info = _get_file_info(func)
    qualname = func.__qualname__
    is_class_function = inspect.ismethod

    identify_args = {}
    for key, value in applied_args.items():
        if key == ("cls" if is_class_function(func) else "self"):
            pass
        elif key in ignore:
            pass
        elif inspect.isclass(value):
            logging.warning(
                f"A class is used as the parameter of {str(value)}, it may cause mistake when detecting whether there is checkpoint for this call.")
            identify_args[key] = value.__qualname__
        elif inspect.ismethod(value) or inspect.isfunction(value):
            logging.warning(
                f"A function is used as the parameter of {str(value)}, it may cause mistake when detecting whether there is checkpoint for this call.")
            tmp_applied_args = _get_applied_args(value, (), {})
            identify_args[key] = _get_name(value, tmp_applied_args)
        elif isinstance(value, pd.DataFrame):
            if value.shape[0] > value.shape[1]:
                identify_args[key] = pd.util.hash_pandas_object(
                    value.T).to_json(orient='values')
            else:
                identify_args[key] = pd.util.hash_pandas_object(
                    value).to_json(orient='values')
        elif isinstance(value, pd.Series):
            identify_args[key] = pd.util.hash_pandas_object(
                pd.DataFrame(value).T).to_json(orient='values')
        elif isinstance(value, np.ndarray):
            if value.flags['C_CONTIGUOUS']:
                identify_args[key] = hashlib.md5(value).hexdigest()
            else:
                identify_args[key] = hashlib.md5(
                    np.ascontiguousarray(value)).hexdigest()
        else:
            identify_args[key] = str(value) + str(type(value))

    identify_args_str = "-".join([k+":"+v for k,
                                  v in identify_args.items()])

    full_str = f"{file_info}-{qualname}-{identify_args_str}"
    logging.debug(f"Identification String: {full_str}")
    return full_str


def _get_hash(str_):
    h = hashlib.md5()
    h.update(str_.encode("utf-8"))
    return h.hexdigest()


def _get_applied_args(func, args, kwargs):
    # Get default args and kwargs
    signature = inspect.signature(func)
    applied_args = OrderedDict({
        k: v.default
        for k, v in signature.parameters.items() if k != "__overwrite__"
    })

    # update call args into applied_args
    items = list(applied_args.items())
    for ix, arg in enumerate(args):
        applied_args[items[ix][0]] = arg
    for key, value in kwargs.items():
        applied_args[key] = value

    return applied_args


def checkpoint(ignore=[]):
    save_dir = ".skutil-checkpoint"

    if callable(ignore):
        param_is_callable = True
        func = ignore
        ignore = []
    elif isinstance(ignore, (list, tuple)):
        param_is_callable = False
    else:
        raise TypeError(f"Unsupported parameter type '{type(ignore)}'")

    def wrapper(func):
        def inner(*args, __overwrite__=False, **kwargs):
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)

            if not isinstance(__overwrite__, bool):
                raise TypeError(
                    "'__overwrite__' parameter must be a boolean type")

            applied_args = _get_applied_args(func, args, kwargs)
            name = _get_name(func, applied_args, ignore)
            hash_val = _get_hash(name)

            cache_path = os.path.join(save_dir, f"{hash_val}.pkl")
            if os.path.exists(cache_path) and not __overwrite__:
                return joblib.load(cache_path)
            else:
                res = func(*args, **kwargs)
                joblib.dump(res, cache_path)
                return res
        return inner

    if param_is_callable:
        return wrapper(func)
    else:
        return wrapper
