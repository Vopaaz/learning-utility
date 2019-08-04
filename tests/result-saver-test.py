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


class ResultSaverGeneralTest(ResultSaverTest):

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

        saver = ResultSaver(save_dir=self.test_assets_dir,
                            save_func=save_func, encoding="utf-8")
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

    def test_save_by_csv_param_error(self):
        with self.assertRaises(ValueError):
            ResultSaver(self.test_assets_dir,
                        example_path=r"tests/assets/data1.csv", encoding="utf-8")

        with self.assertRaises(ValueError):
            saver = ResultSaver(self.test_assets_dir,
                                example_path=r"tests/assets/data1.csv")
            saver.save("Nothing", "some_name.csv", encoding="utf-8")

    def test_save_by_csv_using_kwargs(self):
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [2, 3],
            "c": [3, 4]
        }, index=[9, 10])

        name_1 = "test_save_by_csv_using_kwargs_1.csv"
        content_1 = '''9,1,2,3
10,2,3,4
'''
        saver = ResultSaver(self.test_assets_dir, index=True, header=False)
        saver.save(df, name_1, line_terminator="\n")

        with open(os.path.join(self.test_assets_dir, name_1), "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(content, content_1)

        name_2 = "test_save_by_csv_using_kwargs_2.csv"
        content_2 = '''a;b;c
1;2;3
2;3;4
'''
        saver = ResultSaver(index=False)
        saver.save(df, os.path.join(self.test_assets_dir, name_2), sep=";")

        with open(os.path.join(self.test_assets_dir, name_2), "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(content, content_2)

