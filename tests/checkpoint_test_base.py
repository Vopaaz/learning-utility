import io
import unittest
import sys

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
