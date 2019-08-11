from skutil.IO import InlineCheckpoint
from checkpoint_test_base import R, CheckpointBaseTest


def add_give_c(a, b):
    c = "reset"
    with InlineCheckpoint(watch=["a", "b"], produce=["c"], _id="add_give_c"):
        R()
        c = a + b
    return c


class InlineCheckpointTest(CheckpointBaseTest):
    def test_add_give_c(self):
        self.assertEqual(add_give_c(1,2),1+2)
        self.runned()

        self.assertEqual(add_give_c(1,2),1+2)
        self.not_runned()

        self.assertEqual(add_give_c(1,3),1+3)
        self.runned()

        self.assertEqual(add_give_c(1,3),1+3)
        self.not_runned()
