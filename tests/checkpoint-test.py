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


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.M = io.StringIO()
        sys.stdout = self.M

    def clear(self):
        self.M.truncate(0)
        self.M.seek(0)

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
        self.assertEqual(self.M.getvalue(), RM)
        self.clear()
        self.assertEqual(empty(), 0)
        self.assertEqual(self.M.getvalue(), "")

