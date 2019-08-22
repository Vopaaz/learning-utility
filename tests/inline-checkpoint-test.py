from Lutil.checkpoints import InlineCheckpoint
from checkpoint_test_base import R, CheckpointBaseTest
import numpy as np
import pandas as pd
from Lutil._exceptions import InlineEnvironmentWarning, NotInlineCheckableError

def add_give_c(a, b):
    c = "reset"
    with InlineCheckpoint(watch=["a", "b"], produce=["c"], _id="add_give_c"):
        R()
        c = a + b
    return c

class Foo(object):
    pass

def add_give_c_in_obj(a, b):
    f = Foo()
    f.c = "reset"

    with InlineCheckpoint(watch=["a", "b"], produce=["f.c"], _id="add_give_c"):
        R()
        f.c = a + b

    return f.c

def watch_obj_value(a):
    f = Foo()
    f.a = a

    with InlineCheckpoint(watch=["f.a"], produce=["f.c"], _id="add_give_c"):
        R()
        f.c = a

    return f.c

def fail_1():
    with InlineCheckpoint(watch=["a"], produce=["b"], _id="fail_1"):
        R()
        b = a
    return b

def fail_2():
    f = Foo()
    with InlineCheckpoint(watch=["f.a"], produce=["b"], _id="fail_2"):
        R()
        b = f.a
    return b

def multi_level(a):
    f = Foo()
    f.f = Foo()
    f.f.f = Foo()
    f.f.f.a = a

    with InlineCheckpoint(watch=["f.f.f.a"], produce=["f.f.b"], _id="multi_level"):
        R()
        f.f.b = f.f.f.a
    return f.f.b

def default_id(a):
    f = Foo()
    f.a = a
    with InlineCheckpoint(watch=["f.a"], produce=["f.b"]):
        R()
        f.b = f.a
    return f.b

def no_watch():
    f = Foo()
    with InlineCheckpoint(watch=[], produce=["f.a"]):
        R()
        f.a = 1

    return f.a

def produce_two():
    f = Foo()
    with InlineCheckpoint(watch=[], produce=["f.a", "f.b"]):
        R()
        f.a = 1
        f.b = 2
    return f.a, f.b

class InlineCheckpointTest(CheckpointBaseTest):
    arr3 = np.array([
        [1,2,4,7],
        [2,1,2,2],
    ])

    df3 = pd.DataFrame({
        "a": [1.12],
        "b": [2.1]
    })

    def test_add_give_c(self):
        # with self.assertWarns(InlineEnvironmentWarning):
        self.assertEqual(add_give_c(1,2),1+2)
        self.runned()

        # with self.assertWarns(InlineEnvironmentWarning):
        self.assertEqual(add_give_c(1,3),1+3)
        self.runned()

        # with self.assertWarns(InlineEnvironmentWarning):
        self.assertEqual(add_give_c(1,2),1+2)
        self.runned()

        # with self.assertWarns(InlineEnvironmentWarning):
        self.assertEqual(add_give_c(1,3),1+3)
        self.runned()

    def test_add_give_c_in_obj(self):
        self.assertEqual(add_give_c_in_obj(1,2),1+2)
        self.runned()

        self.assertEqual(add_give_c_in_obj(1,3),1+3)
        self.runned()

        self.assertEqual(add_give_c_in_obj(1,2),1+2)
        self.not_runned()

        self.assertEqual(add_give_c_in_obj(1,3),1+3)
        self.not_runned()

    def test_add_give_c_in_obj_df(self):
        self.assertTrue(
            (add_give_c_in_obj(self.df1,self.df2)==self.df1+self.df2).all().all()
            )
        self.runned()

        self.assertTrue(
            (add_give_c_in_obj(self.df1,self.df3)==self.df1+self.df3).all().all()
            )
        self.runned()

        self.assertTrue(
            (add_give_c_in_obj(self.df1,self.df2)==self.df1+self.df2).all().all()
            )
        self.not_runned()

        self.assertTrue(
            (add_give_c_in_obj(self.df1,self.df3)==self.df1+self.df3).all().all()
            )
        self.not_runned()

    def test_add_give_c_in_obj_arr(self):
        self.assertTrue(
            (add_give_c_in_obj(self.arr1,self.arr2)==self.arr1+self.arr2).all()
            )
        self.runned()

        self.assertTrue(
            (add_give_c_in_obj(self.arr1,self.arr3)==self.arr1+self.arr3).all()
            )
        self.runned()

        self.assertTrue(
            (add_give_c_in_obj(self.arr1,self.arr2)==self.arr1+self.arr2).all()
            )
        self.not_runned()

        self.assertTrue(
            (add_give_c_in_obj(self.arr1,self.arr3)==self.arr1+self.arr3).all()
            )
        self.not_runned()

    def test_raise(self):
        with self.assertRaises(ValueError):
            fail_1()

        with self.assertRaises(ValueError):
            fail_2()

    def test_watch_obj_value(self):
        self.assertEqual(watch_obj_value(1),1)
        self.runned()

        self.assertEqual(watch_obj_value(2),2)
        self.runned()

        self.assertEqual(watch_obj_value(1),1)
        self.not_runned()

        self.assertEqual(watch_obj_value(2),2)
        self.not_runned()

    def test_multi_level(self):
        self.assertEqual(multi_level(1),1)
        self.runned()

        self.assertEqual(multi_level(2),2)
        self.runned()

        self.assertEqual(multi_level(1),1)
        self.not_runned()

        self.assertEqual(multi_level(2),2)
        self.not_runned()

    def test_default_id(self):
        self.assertEqual(default_id(1),1)
        self.runned()

        self.assertEqual(default_id(2),2)
        self.runned()

        self.assertEqual(default_id(1),1)
        self.not_runned()

        self.assertEqual(default_id(2),2)
        self.not_runned()

    def test_no_watch(self):
        self.assertEqual(no_watch(),1)
        self.runned()

        self.assertEqual(no_watch(),1)
        self.not_runned()

    def test_produce_two(self):
        self.assertSequenceEqual(produce_two(), (1,2))
        self.runned()

        self.assertSequenceEqual(produce_two(), (1,2))
        self.not_runned()

    def test_generator(self):
        with self.assertRaises(NotInlineCheckableError):
            def some_generator():
                yield 0

            f = Foo()
            with InlineCheckpoint(watch=["some_generator"], produce=["f.a"]):
                f.a = next(some_generator())

    def test_watch_not_exists(self):
        with self.assertRaises(ValueError):
            with InlineCheckpoint(watch=["a"], produce=["b"]):
                b = 3

        f = Foo()
        with self.assertRaises(ValueError):
            with InlineCheckpoint(watch=["f.a"], produce=["b"]):
                b = 3
