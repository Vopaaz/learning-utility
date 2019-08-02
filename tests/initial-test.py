import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import unittest
from skutil.IO import DatasetReader

class InitialTest(unittest.TestCase):
    def test_OK(self):
        DatasetReader("some_path")
        self.assertEqual(1,1)

if __name__ == "__main__":
    unittest.main()
