import unittest
from skutil.IO import ResultSaver
import logging
import pandas as pd

import os
import shutil


class ResultSaverTest(unittest.TestCase):
    test_assets_dir = r"tests/assets/saverTest"

    @classmethod
    def tearDownClass(cls):
        for the_file in os.listdir(cls.test_assets_dir):
            file_path = os.path.join(cls.test_assets_dir, the_file)
            assert "skutil" not in file_path
            assert "git" not in file_path
            assert ".md" not in file_path
        shutil.rmtree(cls.test_assets_dir)

    def test_create_dir(self):
        ResultSaver(save_dir=self.test_assets_dir)
        self.assertTrue(os.path.isdir(self.test_assets_dir))

    def test_init(self):
        with self.assertRaises(Exception):
            _ = ResultSaver(save_func=lambda X: X.writeline,
                            example_path=r"tests/assets/data1.csv")

        with self.assertRaises(Exception):
            _ = ResultSaver(save_func=isinstance,
                            example_path=r"tests/assets/data1.csv")

        with self.assertRaises(ValueError):
            _ = ResultSaver(save_func=lambda X: X.to_clipboard,
                            example_path=r"tests/assets/data1.csv")

        _ = ResultSaver()
        _ = ResultSaver(save_func=lambda X: X.to_csv)

    def test_save_by_other_func(self):
        data = '''Only some texts.
Only some texts.
Only some texts.
'''

        def save_func(X, path, encoding):
            with open(path, "w", encoding=encoding) as f:
                f.write(str(X))
                return "Success"

        saver = ResultSaver(save_dir=self.test_assets_dir, save_func=save_func, encoding="utf-8")
        res = saver.save(data, "test_save_by_other_func_1.txt")
        with open(os.path.join(self.test_assets_dir, "test_save_by_other_func_1.txt"), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(data, content)
        self.assertEqual(res, "Success")

        saver = ResultSaver(save_dir=self.test_assets_dir, save_func=save_func)
        res = saver.save(data, "test_save_by_other_func_2.txt", encoding="GBK")
        with open(os.path.join(self.test_assets_dir, "test_save_by_other_func_1.txt"), "r", encoding="GBK") as f:
            content = f.read()
        self.assertEqual(data, content)
        self.assertEqual(res, "Success")


