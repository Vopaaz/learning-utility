import os

import joblib
import re

from Lutil.checkpoints._check_util import (_get_applied_args,
                                           _get_hash_of_str,
                                           _get_identify_str_for_func,
                                           _get_file_info,
                                           _get_identify_str_for_value,
                                           _check_handleable,
                                           _check_inline_handleable,
                                           )

from Lutil._exceptions import SkipWithBlock, InlineEnvironmentWarning
import sys
import inspect
import logging
import warnings


_save_dir = ".Lutil-checkpoint"


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
        def inner(*args, **kwargs):
            if not os.path.exists(_save_dir):
                os.mkdir(_save_dir)
            recompute = "__recompute__" in kwargs and kwargs["__recompute__"]
            if recompute:
                kwargs.pop("__recompute__")

            _check_handleable(func)
            file_info = _get_file_info(func)

            applied_args = _get_applied_args(func, args, kwargs)
            id_str = _get_identify_str_for_func(func, applied_args, ignore)
            hash_val = _get_hash_of_str(file_info + id_str)

            cache_path = os.path.join(_save_dir, f"{hash_val}.pkl")

            if os.path.exists(cache_path) and not recompute:
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


class InlineCheckpoint(object):
    def __init__(self, *, watch, produce):
        assert isinstance(watch, (list, tuple))
        assert isinstance(produce, (list, tuple))
        self.watch = watch
        self.produce = produce

        if not os.path.exists(_save_dir):
            os.mkdir(_save_dir)

        call_f = inspect.currentframe().f_back
        self.lineno = call_f.f_lineno
        self.locals = call_f.f_locals
        self.globals = call_f.f_globals

        self.__check_watch_produce()

        status_str = self.__get_status_str()
        self.status_hash = _get_hash_of_str(status_str)

        logging.debug(f"status_str: {status_str}")

        self.skip = self.__check_skip()

    def __get_watch(self, i):
        assert isinstance(i, str)
        e = ValueError(f"{i} is not a valid identifier.")
        ref_list = i.split(".")
        if ref_list[0] not in self.locals:
            raise e
        curr = self.locals[ref_list[0]]
        for ref in ref_list[1:]:
            if not hasattr(curr, ref):
                raise e
            else:
                curr = getattr(curr, ref)
        return curr

    def __check_watch_produce(self):
        for i in self.watch:
            self.__get_watch(i)

        for i in self.produce:
            assert isinstance(i, str)
            e = ValueError(f"{i} is not a valid identifier.")
            pattern = "^[a-zA-Z_][a-zA-Z_0-9]*$"

            if "." in i:
                ref_list = i.split(".")
                if ref_list[0] not in self.locals:
                    raise e
                curr = self.locals[ref_list[0]]
                for ref in ref_list[1:-1]:
                    if not hasattr(curr, ref):
                        raise e
                    else:
                        curr = getattr(curr, ref)

                if not re.compile(pattern).match(ref_list[-1]):
                    raise e
            else:
                if not re.compile(pattern).match(i):
                    raise e

    def __get_start_line_and_indent(self, sourcelines):

        pattern = r'''(\s*)with .*?\(\s*watch\s*=\s*[\[\(]\s*['"]?%s['"]?\s*[\]\)]\s*,\s*produce\s*=\s*[\[\(]\s*['"]%s['"]\s*[\]\)]\s*\).*?:''' % (
            '''['"]\s*,\s*['"]'''.join(self.watch), '''['"]\s*,\s*['"]'''.join(self.produce))

        matcher = re.compile(pattern)

        start_line = res = None

        while not res and self.lineno > 0:
            init_statement = "\n".join(sourcelines[self.lineno-1:])
            res = matcher.match(init_statement)
            self.lineno -= 1

        if res:
            start_line = self.lineno
            indent = res.group(1)

        if start_line is None:
            raise Exception(
                "Failed to check the content in the with-statement.")

        return start_line, indent

    def __get_status_str(self):
        watch_dict = {}

        for i in self.watch:
            value = self.__get_watch(i)
            _check_inline_handleable(value)
            if inspect.ismethod(value) or inspect.isfunction(value):
                watch_dict[i] = _get_identify_str_for_func(value)
            else:
                watch_dict[i] = _get_identify_str_for_value(value)

        watch_str = "-".join([f"{k}:{v}" for k,
                              v in watch_dict.items()])

        if "_ih" in self.globals and "In" in self.globals and "__file__" not in self.globals:
            file_name = "jupyter-notebook"
            source = "\n".join(self.globals["In"])
        elif "__file__" in self.globals:
            file_name = os.path.basename(self.globals["__file__"])
            with open(self.globals["__file__"], "r", encoding="utf-8") as f:
                source = f.read()
        else:
            logging.debug(self.globals)
            raise Exception(
                "Unknown error when detecting jupyter or .py environment.")

        sourcelines = source.split("\n")
        start_line, indent = self.__get_start_line_and_indent(sourcelines)

        with_statement_lines = []
        for i in range(start_line+1, len(sourcelines)):
            line = sourcelines[i]
            pattern = indent+r"\s+\S+"
            matcher = re.compile(pattern)
            if matcher.match(line):
                with_statement_lines.append(line)
            else:
                break

        with_statement = ";".join(
            [i.strip() for i in with_statement_lines]).replace(" ", "")

        identify_str = f"{file_name}-{watch_str}-{with_statement}"
        return identify_str

    def __checkpoint_exists(self):
        for i in self.produce:
            if not os.path.exists(self.__cache_file_name(i)):
                return False
        return True

    def __check_skip(self):
        if "__name__" not in self.locals or self.locals["__name__"] != "__main__":
            for i in self.produce:
                if "." not in i:
                    warnings.warn(InlineEnvironmentWarning())
                    return False

        return self.__checkpoint_exists()

    def __enter__(self):
        if self.skip:
            sys.settrace(lambda *args, **keys: None)
            frame = sys._getframe(1)
            frame.f_trace = self._trace
        return self

    def _trace(self, frame, event, arg):
        raise SkipWithBlock()

    def __exit__(self, type, value, traceback):
        if self.skip:
            for i in self.produce:
                self.__retrieve(i)
        else:
            for i in self.produce:
                self.__save(i)

        if type is None:
            return
        if issubclass(type, SkipWithBlock):
            return True

    def __cache_file_name(self, i):
        return os.path.join(_save_dir, f"{self.status_hash}-{i}.pkl")

    def __retrieve(self, i):
        obj = joblib.load(self.__cache_file_name(i))

        if "." not in i:
            self.locals[i] = obj
        else:
            ref_list = i.split(".")
            curr = self.locals[ref_list[0]]
            for ref in ref_list[1:-1]:
                curr = getattr(curr, ref)

            setattr(curr, ref_list[-1], obj)

    def __save(self, i):
        if "." not in i:
            obj = self.locals[i]
        else:
            ref_list = i.split(".")
            curr = self.locals[ref_list[0]]
            for ref in ref_list[1:]:
                curr = getattr(curr, ref)
            obj = curr

        joblib.dump(obj, self.__cache_file_name(i))
