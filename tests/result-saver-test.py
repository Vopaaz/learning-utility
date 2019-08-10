import unittest
from skutil.IO import AutoSaver
import logging
import pandas as pd
import numpy as np

import os
import shutil

from skutil.IO._exceptions import SpeculationFailedError


class AutoSaverTest(unittest.TestCase):
    test_assets_dir = r"tests/assets/saverTest"

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_assets_dir):
            for the_file in os.listdir(cls.test_assets_dir):
                file_path = os.path.join(cls.test_assets_dir, the_file)
                assert "skutil" not in file_path
                assert "git" not in file_path
                assert ".md" not in file_path
            shutil.rmtree(cls.test_assets_dir)


class AutoSaverGeneralTest(AutoSaverTest):

    def test_create_dir(self):
        AutoSaver(save_dir=self.test_assets_dir)
        self.assertTrue(os.path.isdir(self.test_assets_dir))

    def test_save_by_csv_param_error(self):
        with self.assertRaises(ValueError):
            AutoSaver(self.test_assets_dir,
                        example_path=r"tests/assets/data1.csv", encoding="utf-8")

        with self.assertRaises(ValueError):
            saver = AutoSaver(self.test_assets_dir,
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
        saver = AutoSaver(self.test_assets_dir, index=True, header=False)
        saver.save(df, name_1, line_terminator="\n")
        with open(os.path.join(self.test_assets_dir, name_1), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content, content_1)

        name_2 = "test_save_by_csv_using_kwargs_2.csv"
        content_2 = '''a;b;c
1;2;3
2;3;4
'''
        saver = AutoSaver(index=False)
        saver.save(df, os.path.join(self.test_assets_dir, name_2), sep=";")
        with open(os.path.join(self.test_assets_dir, name_2), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content, content_2)

        saver = AutoSaver(index=True, sep=",")
        saver.save(df, os.path.join(self.test_assets_dir, name_2), sep=";", index=False)
        with open(os.path.join(self.test_assets_dir, name_2), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content, content_2)


    def test_memo(self):
        saver = AutoSaver(self.test_assets_dir)
        saver.save(pd.DataFrame(), "test_memo_df.csv", "hello")
        with open(os.path.join(self.test_assets_dir, "memo.txt"), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content.strip(), "test_memo_df.csv: hello")

        saver.save(pd.DataFrame(), "test_memo_df_2.csv", "hello again")
        with open(os.path.join(self.test_assets_dir, "memo.txt"), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content.strip(), "\n".join(
            ["test_memo_df.csv: hello", "test_memo_df_2.csv: hello again"]))


class AutoSaverSpeculatingTest(AutoSaverTest):
    np_1d = np.array([1, 0, 1.5, 0.5])
    np_2d_1val = np.array([[1], [0], [1.5], [0.5]])

    # Just for creating DataFrame, not used as Test
    np_2d_ix_and_val = np.array([
        [0, 1, 2, 3],
        [1, 0, 1.5, 0.5]
    ]).T
    np_2d_ix_start_1_and_val = np.array([
        [1, 2, 3, 4],
        [1, 0, 1.5, 0.5]
    ]).T

    pd_series = pd.Series(np_1d)
    pd_series_with_name = pd.Series(np_1d, name="name")
    pd_series_with_ix_start_1 = pd.Series(
        np_1d, index=np_2d_ix_start_1_and_val[:, 0])
    pd_series_with_bad_index = pd.Series(
        np_1d, index=[7, 3, 2, 9])

    pd_df_1d = pd.DataFrame(np_1d)
    pd_df_1d_ix_and_val = pd.DataFrame(
        np_1d, index=np_2d_ix_start_1_and_val[:, 0])
    pd_df_2d = pd.DataFrame(np_2d_ix_and_val)
    pd_df_2d_start_1 = pd.DataFrame(np_2d_ix_start_1_and_val)

    filename = "temp_writing.csv"

    def test_saving_without_example_path(self):
        saver = AutoSaver(self.test_assets_dir)
        with self.assertRaises(TypeError):
            saver.save(self.np_1d, "wrong.csv")

        saver.save(self.pd_df_1d, "test_saving_without_example_path_1.csv")
        self.pd_df_1d.to_csv(os.path.join(
            self.test_assets_dir, "test_saving_without_example_path_2.csv"))

        with open(os.path.join(self.test_assets_dir, "test_saving_without_example_path_1.csv"), "r", encoding="utf-8") as f:
            content_1 = f.read()
        with open(os.path.join(self.test_assets_dir, "test_saving_without_example_path_2.csv"), "r", encoding="utf-8") as f:
            content_2 = f.read()

        self.assertEqual(content_1, content_2)

    def get_csv_content(self):
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="utf-8") as f:
            return f.read()

    def run_all_X_s(self, saver, target):
        saver.save(self.np_1d, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.np_2d_1val, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_series, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_series_with_name, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_series_with_bad_index, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_series_with_ix_start_1, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_df_1d, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_df_1d_ix_and_val, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_df_2d, self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(self.pd_df_2d_start_1, self.filename)
        self.assertEqual(self.get_csv_content(), target)

    def test_basic(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-basic.csv")
        target = '''index,value
0,1.0
1,0.0
2,1.5
3,0.5
'''
        self.run_all_X_s(saver, target)

    def test_GBK(self):
        # REMINDER: do not use self.get_csv_content when testing GBK.
        # It defaultly uses utf-8.
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-GBK.csv")
        target = '''index,value
0,1.0
1,0.0
2,1.5
3,0.5
'''
        saver.save(self.np_1d, self.filename)
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="GBK") as f:
            content = f.read()
        self.assertEqual(content, target)

        saver.save(self.np_2d_1val, self.filename)
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="GBK") as f:
            content = f.read()
        self.assertEqual(content, target)

        saver.save(self.pd_df_2d, self.filename)
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="GBK") as f:
            content = f.read()
        self.assertEqual(content, target)

    def test_other_sep(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-other-sep.csv")
        target = '''index;value
0;1.0
1;0.0
2;1.5
3;0.5
'''

        self.run_all_X_s(saver, target)

    def test_str_as_index(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-str-as-index.csv")

        str_ix = ["strix1", "strix2", "strix3", "strix4"]

        with self.assertRaises(SpeculationFailedError):
            saver.save(self.np_1d, self.filename)

        with self.assertRaises(SpeculationFailedError):
            saver.save(self.pd_df_1d, self.filename)

        saver.save(self.pd_df_2d, self.filename)
        target = '''ix,val
0,1.0
1,0.0
2,1.5
3,0.5
'''
        self.assertEqual(self.get_csv_content(), target)

        saver.save(pd.Series(self.np_1d, index=str_ix), self.filename)
        target = '''ix,val
strix1,1.0
strix2,0.0
strix3,1.5
strix4,0.5
'''
        self.assertEqual(self.get_csv_content(), target)

        saver.save(pd.DataFrame(self.np_1d, index=str_ix), self.filename)
        self.assertEqual(self.get_csv_content(), target)

        saver.save(pd.DataFrame({
            "ix": str_ix,
            "val": self.np_1d,
        }), self.filename)
        self.assertEqual(self.get_csv_content(), target)

    def test_saving_two_value(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-two-value.csv")
        arr = np.array([
            [1,1.5],
            [0.5,0.7],
            [0.2,0.3]
        ])

        df = pd.DataFrame(arr)

        target = '''ix,val1,val2
0,1.0,1.5
1,0.5,0.7
2,0.2,0.3
'''
        saver.save(arr, self.filename)
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, target)

        saver.save(df, self.filename)
        with open(os.path.join(self.test_assets_dir, self.filename), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, target)

    def test_saving_without_head(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-without-head.csv")
        target = '''0,1.0
1,0.0
2,1.5
3,0.5
'''

        self.run_all_X_s(saver, target)

    def test_saving_without_index(self):
        saver = AutoSaver(save_dir=self.test_assets_dir,
                            example_path=r"tests/assets/saver-example-without-index.csv")
        target = '''1.0
0.0
1.5
0.5
'''

        self.run_all_X_s(saver, target)
