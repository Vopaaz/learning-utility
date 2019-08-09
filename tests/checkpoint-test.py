import unittest
from skutil.IO import checkpoint
from unittest.mock import MagicMock
import io
import sys
import os
import shutil

RM = "Runned."


def R():
    print(RM, end="")


@checkpoint
def empty():
    R()
    return 0

@checkpoint
def adding(a,b):
    R()
    return a+b

@checkpoint
def adding_with_default(a,b=3):
    R()
    return a+b


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
        self.assertEqual(adding(2,3),2+3)
        self.runned()

        self.assertEqual(adding(3,3),3+3)
        self.runned()

        self.assertEqual(adding(2,3),2+3)
        self.not_runned()

        self.assertEqual(adding(2.0,3.0),2.0+3.0)
        self.runned()

    def test_adding_with_default(self):
        self.assertEqual(adding_with_default(2,3),2+3)
        self.runned()

        self.assertEqual(adding_with_default(3),3+3)
        self.runned()

        self.assertEqual(adding_with_default(2),2+3)
        self.not_runned()

        self.assertEqual(adding_with_default(2,3),2+3)
        self.not_runned()
