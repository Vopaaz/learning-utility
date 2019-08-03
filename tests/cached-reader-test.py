import unittest
from skutil.IO import CachedDataReader
import logging
import pandas as pd


class CachedDataReaderTest(unittest.TestCase):
    def setUp(self):
        self.path1 = r"tests/assets/data1.csv"
        self.path2 = r"tests/assets/data2.csv"
        self.path3 = r"tests/assets/data3.csv"

    def test_singleton(self):
        reader1 = CachedDataReader()
        reader2 = CachedDataReader()
        self.assertTrue(reader1 is reader2)

        reader3 = CachedDataReader(_id="test_singleton")
        self.assertTrue(reader1 is not reader3)

        reader4 = CachedDataReader(_id="test_singleton")
        self.assertTrue(reader3 is reader4)

    def test_get_set_path_with_init(self):
        train_path = self.path1
        test_path = self.path2
        val_path = self.path3

        reader = CachedDataReader(
            train_path, test_path, val_path, _id="test_get_set_path_with_init")

        self.assertEqual(reader.train_path, train_path)
        with self.assertRaises(ValueError):
            reader.train_path = test_path
        with self.assertLogs(level=logging.INFO):
            reader.train_path = train_path

        self.assertEqual(reader.test_path, test_path)
        with self.assertRaises(ValueError):
            reader.test_path = train_path
        with self.assertLogs(level=logging.INFO):
            reader.test_path = test_path

        self.assertEqual(reader.val_path, val_path)
        with self.assertRaises(ValueError):
            reader.val_path = train_path
        with self.assertLogs(level=logging.INFO):
            reader.val_path = val_path

    def test_get_set_path_without_init(self):
        train_path = self.path1
        test_path = self.path2
        val_path = self.path3

        reader = CachedDataReader(_id="test_get_set_path_without_init")

        with self.assertRaises(AttributeError):
            _ = reader.train_path
        with self.assertLogs(level=logging.WARNING):
            reader.train_path = train_path
        with self.assertRaises(ValueError):
            reader.train_path = test_path
        self.assertEqual(reader.train_path, train_path)

        with self.assertRaises(AttributeError):
            _ = reader.test_path
        with self.assertLogs(level=logging.WARNING):
            reader.test_path = test_path
        with self.assertRaises(ValueError):
            reader.test_path = train_path
        self.assertEqual(reader.test_path, test_path)

        with self.assertRaises(AttributeError):
            _ = reader.val_path
        with self.assertLogs(level=logging.WARNING):
            reader.val_path = val_path
        with self.assertRaises(ValueError):
            reader.val_path = train_path
        self.assertEqual(reader.val_path, val_path)

    def test_initial_read_func_and_read_config(self):
        _id = "test_initial_read_func_and_read_config"

        reader = CachedDataReader(
            self.path1, _id=_id+"1", conf_a="a", conf_b="B")
        self.assertTrue(reader._CachedDataReader__read_func is pd.read_csv)
        self.assertDictEqual(reader._CachedDataReader__read_config, {
                             "conf_a": "a", "conf_b": "B"})

        reader = CachedDataReader(
            self.path1, _id=_id+"2", read_func=pd.read_clipboard)
        self.assertTrue(
            reader._CachedDataReader__read_func is pd.read_clipboard)

    def test_duplicate_init(self):
        _id = "test_duplicate_init"
        _ = CachedDataReader(self.path1, _id=_id, c_conf="some_conf")

        with self.assertRaises(ValueError):
            _ = CachedDataReader(self.path2, _id=_id)

        with self.assertLogs(level=logging.WARNING):
            _ = CachedDataReader(self.path1, self.path2, _id=_id)

        with self.assertRaises(ValueError):
            _ = CachedDataReader(self.path1, _id=_id, c_conf="some_else")

        with self.assertRaises(ValueError):
            _ = CachedDataReader(self.path1, _id=_id,
                                 c_conf="some_conf", c_conf_2="some_2")

        with self.assertLogs(level=logging.INFO):
            _ = CachedDataReader(self.path1, _id=_id)

        with self.assertLogs(level=logging.INFO):
            _ = CachedDataReader(self.path1, _id=_id, c_conf="some_conf")

        with self.assertLogs(level=logging.INFO):
            _ = CachedDataReader(_id=_id, c_conf="some_conf")

        with self.assertRaises(ValueError):
            _ = CachedDataReader(read_func=pd.read_excel, _id=_id)

        with self.assertLogs(level=logging.INFO):
            _ = CachedDataReader(read_func=pd.read_csv, _id=_id)

    def test_csv_reading(self):
        _id = "test_csv_reading"
        reader1 = CachedDataReader(self.path1, _id=_id+"1")
        self.assertTrue(
            (
                reader1.train == pd.read_csv(self.path1)
            ).all().all()
        )

        self.assertTrue(
            (
                reader1.train.index == pd.read_csv(self.path1).index
            ).all()
        )

        self.assertTrue(
            (
                reader1.train.columns == pd.read_csv(self.path1).columns
            ).all()
        )

        reader2 = CachedDataReader(
            val_path=self.path2, _id=_id+"2", index_col="car")
        self.assertTrue(
            (
                reader2.val == pd.read_csv(self.path2, index_col="car")
            ).all().all()
        )

        self.assertTrue(
            (
                reader2.val.index == pd.read_csv(
                    self.path2, index_col="car").index
            ).all()
        )

        self.assertTrue(
            (
                reader2.val.columns == pd.read_csv(
                    self.path2, index_col="car").columns
            ).all()
        )

        reader_all = CachedDataReader(
            self.path1, self.path2, self.path3, _id=_id+"all")

        self.assertTrue(
            (
                reader_all.train == pd.read_csv(self.path1)
            ).all().all()
        )

        self.assertTrue(
            (
                reader_all.test == pd.read_csv(self.path2)
            ).all().all()
        )

        self.assertTrue(
            (
                reader_all.val == pd.read_csv(self.path3)
            ).all().all()
        )

    def test_duplicate_csv_reading(self):
        _id = "test_duplicate_csv_reading"

        reader1 = CachedDataReader(self.path1, _id=_id)
        reader2 = CachedDataReader(self.path1, _id=_id)
        reader3 = CachedDataReader(_id=_id)

        self.assertTrue(reader1.train is reader2.train)
        self.assertTrue(reader2.train is reader3.train)

    def test_delay_set_path_and_read(self):
        _id="test_delay_set_path_and_read"
        reader = CachedDataReader(_id=_id)

        with self.assertRaises(AttributeError):
            _ = reader.train

        reader.train_path = self.path1
        _ = reader.train

if __name__ == "__main__":
    unittest.main()
