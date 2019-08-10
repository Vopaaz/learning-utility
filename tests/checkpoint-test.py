import io
import os
import shutil
import sys
import unittest
import pandas as pd
import numpy as np

from skutil.IO import checkpoint

RM = "Runned."


def R():
    print(RM, end="")


@checkpoint
def empty():
    R()
    return 0


@checkpoint
def adding(a, b):
    R()
    return a+b


@checkpoint
def adding_with_default(a, b=3):
    R()
    return a+b


@checkpoint(ignore=["a"])
def adding_with_ignore(a, b=3):
    R()
    return a+b

@checkpoint
def df_as_input(df):
    R()
    return df

@checkpoint
def numpy_as_input(arr):
    R()
    return arr

class Foo(object):
    def __init__(self):
        self.a = 1

    @checkpoint
    def no_args(self):
        R()
        return self.a

    @checkpoint
    def with_args(self,b):
        R()
        return self.a + b

    @classmethod
    @checkpoint
    def class_method(cls,a):
        R()
        return a


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.M = io.StringIO()
        sys.stdout = self.M

    def clear(self):
        self.M.truncate(0)
        self.M.seek(0)

    def runned(self):
        self.assertEqual(self.M.getvalue(), RM)
        self.clear()

    def not_runned(self):
        self.assertEqual(self.M.getvalue(), "")
        self.clear()

    def tearDown(self):
        sys.stdout = sys.__stdout__
        dir_name = ".skutil-checkpoint"
        sub_dir_name = os.path.join("tests", dir_name)
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

        if os.path.exists(sub_dir_name):
            shutil.rmtree(sub_dir_name)

    def test_empty(self):
        self.assertEqual(empty(), 0)
        self.runned()

        self.assertEqual(empty(), 0)
        self.not_runned()

    def test_adding(self):
        self.assertEqual(adding(2, 3), 2+3)
        self.runned()

        self.assertEqual(adding(3, 3), 3+3)
        self.runned()

        self.assertEqual(adding(2, 3), 2+3)
        self.not_runned()

        self.assertEqual(adding(2.0, 3.0), 2.0+3.0)
        self.runned()

    def test_adding_with_default(self):
        self.assertEqual(adding_with_default(2, 3), 2+3)
        self.runned()

        self.assertEqual(adding_with_default(3), 3+3)
        self.runned()

        self.assertEqual(adding_with_default(2), 2+3)
        self.not_runned()

        self.assertEqual(adding_with_default(2, 3), 2+3)
        self.not_runned()

    def test_ignore(self):
        self.assertEqual(adding_with_ignore(2, 3), 2+3)
        self.runned()

        self.assertEqual(adding_with_ignore(3, 3), 2+3)
        self.not_runned()

        self.assertEqual(adding_with_ignore(3, 4), 3+4)
        self.runned()

        self.assertEqual(adding_with_ignore(123), 2+3)
        self.not_runned()

    def test_df_as_input(self):
        df1 = pd.DataFrame({
            "a":[1],
            "b":[2]
        })

        self.assertTrue((df_as_input(df1)==df1).all().all())
        self.runned()

        self.assertTrue((df_as_input(df1)==df1).all().all())
        self.not_runned()

        df2 = pd.DataFrame({
            "a":[1],
            "b":[2.1]
        })

        self.assertTrue((df_as_input(df2)==df2).all().all())
        self.runned()

        self.assertTrue((df_as_input(df2)==df2).all().all())
        self.not_runned()

    def test_numpy_as_input(self):
        arr1 = np.array([
            [1],
            [2]
        ])

        self.assertTrue((numpy_as_input(arr1)==arr1).all())
        self.runned()

        self.assertTrue((numpy_as_input(arr1)==arr1).all())
        self.not_runned()

        arr2 = np.array([
            [1,1],
            [2,2]
        ])

        self.assertTrue((numpy_as_input(arr2)==arr2).all())
        self.runned()

        self.assertTrue((numpy_as_input(arr2)==arr2).all())
        self.not_runned()

    def test_method(self):
        f = Foo()
        self.assertEqual(f.no_args(),f.a)
        self.runned()

        self.assertEqual(f.no_args(),f.a)
        self.not_runned()

        self.assertEqual(f.with_args(3),f.a+3)
        self.runned()

        self.assertEqual(f.with_args(3),f.a+3)
        self.not_runned()

        f.a=2
        self.assertEqual(f.no_args(),f.a)
        self.runned()

        self.assertEqual(f.with_args(3),f.a+3)
        self.runned()

    def test_class_method(self):
        self.assertEqual(Foo.class_method(1),1)
        self.runned()

        self.assertEqual(Foo.class_method(1),1)
        self.not_runned()

        self.assertEqual(Foo.class_method(2.5),2.5)
        self.runned()

        self.assertEqual(Foo.class_method(2.5),2.5)
        self.not_runned()
