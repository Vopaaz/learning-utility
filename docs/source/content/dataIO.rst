dataIO: Read Data, Save Result
=============================================

.. contents::

.. py:module:: Lutil.dataIO


AutoSaver, Auto-format and Save Prediction Results
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

In some machine learning competitions, like `kaggle <https://www.kaggle.com/>`_,
a .csv file is required for result submission.
Its format is usually illustrated in an example file.
``AutoSaver`` inspects the required format from the example, and
save your result.

.. py:class:: AutoSaver(save_dir="", example_path=None, **default_kwargs)

    :param str save_dir: Directory where your results will be saved
    :param str example_path: Optional, path to the example .csv file
    :param default_kwargs: Default keyword arguments arbitrarily used for `DataFrame.to_csv()`

.. py:method:: Autosaver.save(self, X, filename, memo=None, **kwargs)

    :param X: The prediction result to be saved
    :type X: pd.DataFrame, pd.Series or np.ndarray
    :param str filename: The filename of the result file
    :param str memo: Optional, the memo logged for this result
    :param kwargs: Other keyword arguments arbitrarily used for `DataFrame.to_csv()`


Auto-format Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have provided the simplest example in
`the welcome page <../index.html#save-prediction-result-according-to-the-given-format>`_.
More format and data types can be inferred.

For example, if the index in the example starts from zero and there is no headers

.. code-block:: text

    0, 0.1
    1, 0.1
    2, 0.1

Run:

.. code-block:: python

    >>> import numpy as np
    >>> from Lutil.dataIO import AutoSaver

    >>> result = np.array([0.2, 0.4, 0.1, 0.5])
            # Typical output of a scikit-learn predictor

    >>> ac = AutoSaver(save_dir="somedir", example_path="path/to/example.csv")
    >>> ac.save(result, "some_name.csv")

Then in your somedir/some_name.csv:

.. code-block:: text

    0, 0.2
    1, 0.4
    2, 0.1
    3, 0.5

Some competitions use a hash-like value as the index. For instance, in your example.csv:

.. code-block:: text

    hash, value
    aaffc2, 0.1
    spf2oa, 0.1
    as2nw2, 0.1

Then you should include the index in the ``X`` parameter.
However, how you achieve this is quite at will.

.. code-block:: python

    >>> import numpy as np
    >>> import pandas as pd
    >>> from Lutil.dataIO import AutoSaver

    >>> index = ["aaffc2", "spf2oa", "as2nw2", "wn2ajn"]
    >>> pred = np.array([0.2, 0.4, 0.1, 0.5])

    >>> # In either of the four ways:
    >>> result = pd.Series(pred, index=index)
    >>> result = pd.DataFrame({
    ...     "ix": index,
    ...     "pred": pred
    ... })
    >>> result = pd.DataFrame({"pred":pred}, index=index)
    >>> result = np.array([index, pred]).T

    >>> ac = AutoSaver(save_dir="somedir", example_path=r"explore\doctests\example.csv")
    >>> ac.save(result, "some_name.csv")

In your somedir/some_name.csv, the results will be perfectly saved:

.. code-block:: text

    hash,value
    aaffc2,0.2
    spf2oa,0.4
    as2nw2,0.1
    wn2ajn,0.5

As long as the object you are saving is a numpy.ndarray or a pd.Series/pd.DataFrame,
and it "looks like" the final csv file according to the example, the auto-format will work.


Log Memo for the Results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you would like a memo, a description for the results you have saved.
Then you can use the ``memo`` parameter in the ``AutoSaver.save`` method.


.. code-block:: python

    >>> result1 = np.array([0.2, 0.4, 0.1, 0.5])
    >>> result2 = np.array([0.2, 0.3, 0.1, 0.6])

    >>> ac = AutoSaver(save_dir="somedir", example_path="path/to/example.csv")

    >>> ac.save(result1, "result1.csv", memo="Using Random Forest.")
    >>> ac.save(result2, "result2.csv", memo="Using XGBoost.")

Then you will find this in your somedir/memo.txt::

    result1.csv: Using Random Forest.
    result2.csv: Using XGBoost.

All the new memos will be appended to the end of memo.txt.


Arbitrarily Using Keyword Arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the format in your example.csv is too complex and ``AutoSaver`` failed to inspect that,
you can also pass a pandas.Series or pandas.DataFrame to the ``save`` method,
and arbitrarily assign arguments to use its ``to_csv`` method.

It is true that this is not very meaningful,
comparing with directly calling ``DataFrame.to_csv``,
except that it gives you the access to our "memo" feature,
and only have to set the parameters once while saving multiple results.

For example:

.. code-block:: python

    >>> df = pd.DataFrame({
    ...     "ix":[1,2,3],
    ...     "pred":[0.1,0.2,0.3]
    ... })
    >>> ac = AutoSaver(save_dir="somedir", index=False)
    >>> ac.save(df, "result1.csv")

This is equivalent to:

.. code-block:: python

    >>> df.to_csv("somedir/result1.csv", index=False)

You can also add more arguments when calling ``save``:

.. code-block:: python

    >>> ac.save(df, "result2.csv", header=True)

This is equivalent to:

.. code-block:: python

    >>> df.to_csv("somedir/result2.csv", index=True, header=True)

When you use arbitrary arguments, you cannot use the ``example_path`` feature.
They contradicts each other.

DataReader, Raw Data Management
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

If you want to read the dataset multiple times or across modules, it can be boring
to copy-paste your ``pd.read_csv()`` statement. ``DataReader`` is a
dataset manager which allows you to set the reading parameter only once, and
retrieve the raw dataset anytime without more effort.

.. py:class:: DataReader(train_path=None, test_path=None, val_path=None, _id="default", read_func=None, **read_kwargs)

    :param str train_path: Optional, path to the train set
    :param str test_path: Optional, path to the test set
    :param str val_path: Optional, path to the validation set
    :param str _id: Optional, identifier for multiple datasets
    :param callable read_func: Optional, function used for reading data, default ``pd.read_csv``
    :param read_kwargs: Other keyword arguments for applying to the ``read_func``

.. py:attribute:: DataReader.train

    Read only. Each time you access this attribute, the train dataset will be read
    using the ``read_func`` and ``read_kwargs``

.. py:attribute:: DataReader.test

    Read only. Each time you access this attribute, the test dataset will be read
    using the ``read_func`` and ``read_kwargs``

.. py:attribute:: DataReader.val

    Read only. Each time you access this attribute, the validation dataset will be read
    using the ``read_func`` and ``read_kwargs``


Basic Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, ``pandas.read_csv`` will be used to read csv datasets,
whose path are assigned when initializing the ``DataReader`` object.
You can also assign the parameters for ``read_csv`` when initializing.

.. code-block:: python

    >>> from Lutil.dataIO import DataReader


