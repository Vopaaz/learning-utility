import io
import unittest
import sys
import os
import shutil

RM = "Runned."


def R():
    print(RM, end="")


class CheckpointBaseTest(unittest.TestCase):
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
