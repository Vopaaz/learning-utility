import os

import joblib

from skutil.IO._check_util import (_get_applied_args,
                                   _get_hash_of_str,
                                   _get_identify_str_for_func)


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
            id_str = _get_identify_str_for_func(func, applied_args, ignore)
            hash_val = _get_hash_of_str(id_str)

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
