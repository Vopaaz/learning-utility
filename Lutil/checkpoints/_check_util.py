import hashlib
import inspect
import logging
import os
import re
from collections import OrderedDict

import numpy as np
import pandas as pd
import warnings

from Lutil._exceptions import NotDecoratableError, ComplexParamsIdentifyWarning, NotInlineCheckableError


def _get_file_info(obj):
    filename = inspect.getfile(obj)
    ipython_filename_pattern = r"<ipython-input-\d+-(.{12})>"
    ipython_result = re.compile(ipython_filename_pattern).match(filename)
    if ipython_result:
        file_info = f"ipynb-{ipython_result.group(1)}"
    else:
        file_info, _ = os.path.splitext(os.path.basename(filename))

    return file_info


def _get_identify_str_for_cls_or_object(obj):
    identify_dict = {}
    for attr in dir(obj):
        if attr.startswith("__") and attr.endswith("__"):
            pass
        else:
            value = getattr(obj, attr)
            if inspect.ismethod(value) or inspect.isclass(value) or inspect.isfunction(value) or inspect.isbuiltin(value):
                pass
            elif isinstance(value, (pd.DataFrame, pd.Series)):
                identify_dict[attr] = _hash_pd_object(value)
            elif isinstance(value, np.ndarray):
                identify_dict[attr] = _hash_np_array(value)
            else:
                str_val = str(value)
                if re.compile(r"<.*? object at \w{12,20}>").match(str_val):
                    warnings.warn(ComplexParamsIdentifyWarning(
                        f"A complicated object is an attribute of {str(obj)}"))
                else:
                    identify_dict[attr] = str_val + str(type(value))

    return "-".join([k+":"+v for k, v in identify_dict.items()])


def _hash_pd_object(obj):
    try:
        return hashlib.md5(pd.util.hash_pandas_object(obj, index=True).values).hexdigest()
    except TypeError:
        return hashlib.md5(
            pd.util.hash_pandas_object(obj.applymap(
                _get_identify_str_for_value), index=True).values
        ).hexdigest()


def _hash_np_array(arr):
    return "numpy" + str(type(arr)) + _hash_pd_object(pd.DataFrame(arr))


def _get_identify_str_for_value(value):
    if isinstance(value, (pd.DataFrame, pd.Series)):
        return _hash_pd_object(value)

    elif isinstance(value, np.ndarray):
        return _hash_np_array(value)

    else:
        str_val = str(value)
        if re.compile(r"<.*? object at \w{12,20}>").match(str_val):
            return _get_identify_str_for_cls_or_object(value)
        else:
            return str_val + str(type(value))


def _is_general_handleable(obj):
    return not (inspect.isgenerator(obj) or
                inspect.isgeneratorfunction(obj) or
                inspect.iscoroutine(obj) or
                inspect.iscoroutinefunction(obj) or
                inspect.isasyncgen(obj) or
                inspect.isasyncgenfunction(obj)
                )


def _check_handleable(obj):
    if not _is_general_handleable(obj):
        raise NotDecoratableError(obj)


def _check_inline_handleable(obj):
    if not _is_general_handleable(obj):
        raise NotInlineCheckableError(obj)


def _get_identify_str_for_func(func, applied_args, ignore=[]):
    qualname = func.__qualname__

    identify_args = {}
    for key, value in applied_args.items():
        if key in ignore:
            pass

        elif key in ("cls", "self"):
            identify_args[key] = _get_identify_str_for_cls_or_object(value)

        elif inspect.isclass(value):
            warnings.warn(ComplexParamsIdentifyWarning(
                f"A class is used as the parameter"))
            identify_args[key] = value.__qualname__

        elif inspect.ismethod(value) or inspect.isfunction(value):
            warnings.warn(ComplexParamsIdentifyWarning(
                f"A function is used as the parameter"))
            tmp_applied_args = _get_applied_args(value, (), {})
            identify_args[key] = _get_identify_str_for_func(
                value, tmp_applied_args)

        else:
            identify_args[key] = _get_identify_str_for_value(value)

    identify_args_str = "-".join([f"{k}:{v}" for k,
                                  v in identify_args.items()])

    code = inspect.getsource(func).replace("\n", "").replace(" ", "")

    full_str = f"{qualname}-{identify_args_str}-{code}"
    logging.debug(f"Identification String: {full_str}")
    return full_str


def _get_hash_of_str(str_):
    h = hashlib.md5()
    h.update(str_.encode("utf-8"))
    return h.hexdigest()


def _get_applied_args(func, args, kwargs):
    # Get default args and kwargs
    signature = inspect.signature(func)
    applied_args = OrderedDict({
        k: v.default
        for k, v in signature.parameters.items()
    })

    # update call args into applied_args
    items = list(applied_args.items())
    for ix, arg in enumerate(args):
        applied_args[items[ix][0]] = arg
    for key, value in kwargs.items():
        applied_args[key] = value

    return applied_args
