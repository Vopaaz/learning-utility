import os

import joblib
import re

from skutil.IO._check_util import (_get_applied_args,
                                   _get_hash_of_str,
                                   _get_identify_str_for_func,
                                   _get_file_info,
                                   _get_identify_str_for_cls_or_object,
                                   _get_identify_str_for_value,
                                   _check_handleable,
                                   _check_inline_handleable
                                   )

from skutil.IO._exceptions import SkipWithBlock
import sys
import inspect
import logging

_save_dir = ".skutil-checkpoint"
    save_dir = ".skutil-checkpoint"


def checkpoint(ignore=[]):
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
            if not os.path.exists(_save_dir):
                os.mkdir(_save_dir)

            if not isinstance(__overwrite__, bool):
                raise TypeError(
                    "'__overwrite__' parameter must be a boolean type")

            _check_handleable(func)
            file_info = _get_file_info(func)

            applied_args = _get_applied_args(func, args, kwargs)
            id_str = _get_identify_str_for_func(func, applied_args, ignore)
            hash_val = _get_hash_of_str(file_info + id_str)

            cache_path = os.path.join(_save_dir, f"{hash_val}.pkl")
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
