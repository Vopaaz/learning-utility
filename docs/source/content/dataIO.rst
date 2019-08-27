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

Both the keyword arguments assigned when initializing and when calling ``save`` will be applied,
which is equivalent to:

.. code-block:: python

    >>> df.to_csv("somedir/result2.csv", index=True, header=True)

When you use arbitrary arguments, you cannot use the ``example_path`` feature.
They contradicts each other.



DataReader, Raw Data Management
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

If you want to read the dataset multiple times or across modules, it can be boring
to copy-paste your ``pd.read_csv()`` statement. ``DataReader`` is a
dataset manager which allows you to set the reading parameter only once, and
get the dataset anytime after without more effort.

.. py:class:: DataReader(train_path=None, test_path=None, val_path=None, _id="default", read_func=None, **read_kwargs)

    :param str train_path: Optional, path to the train set
    :param str test_path: Optional, path to the test set
    :param str val_path: Optional, path to the validation set
    :param str _id: Optional, identifier for multiple datasets
    :param callable read_func: Optional, function used for reading data, default ``pd.read_csv``
    :param read_kwargs: Other keyword arguments for applying to the ``read_func``

.. py:function:: DataReader.train(self)

    Returns the train set.

.. py:function:: DataReader.test(self)

    Returns the test set.

.. py:function:: DataReader.val(self)

    Returns the validation set.


Basic Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, ``pandas.read_csv`` will be used to read csv datasets,
whose path are assigned when initializing the ``DataReader`` object.
You can also assign the parameters for ``read_csv`` when initializing.

.. code-block:: python

    >>> from Lutil.dataIO import DataReader

    >>> reader = DataReader("path/to/train.csv",
    ...                     "path/to/test.csv",
    ...                     "path/to/val.csv", index_col=1)

    >>> train = reader.train()

This is equivalent to::

    >>> train = pd.read_csv("path/to/train.csv", index_col=1)

Likewise, you can also call

.. code-block:: python

    >>> test = reader.test()
    >>> val = reader.val()

which are equivalent to::

    >>> test = pd.read_csv("path/to/test.csv", index_col=1)
    >>> val = pd.read_csv("path/to/val.csv", index_col=1)

Ever since you have initialized one instance, you can completely forget about the
object and all parameter configurations.
In the same runtime, even in other files,
this will be able to retrieve the train set as before.

.. code-block:: python

    >>> DataReader().train()

It is the same for the test set and the validation set.


Accessing Multiple Datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most small-scale machine learning tasks only have one dataset,
which is our basic usage.
However, if you want to access multiple datasets, you can assign the ``_id`` parameter.
This will work accross files as well.


.. code-block:: python

    >>> DataReader("path/to/train_1.csv", _id="1", index_col=1)
    >>> DataReader("path/to/train_2.csv", _id="2", nrows=500)

    >>> train_1 = DataReader(_id="1").train()
    >>> # Equivalent to
    >>> train_1 = pd.read_csv("path/to/train_1.csv", index_col=1)

    >>> train_2 = DataReader(_id="2").train()
    >>> # Equivalent to
    >>> train_2 = pd.read_csv("path/to/train_2.csv", nrows=500)


Using other Reading Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the data source is not a csv file, and you want to read them with other functions,
you can pass a callable to the ``read_func`` parameter.

.. code-block:: python

    >>> import pandas as pd
    >>> reader = DataReader("path/to/train.json", read_func=pd.read_json)
    >>> train = reader.train()

This is equivalent to::

    >>> train = pd.read_json("path/to/train.json")

Applying other keyword parameter is the same as before, pass them when initializing
the ``DataReader`` object and it will be passed when actually calling the ``read_func``.

As you see, this will only work if the dataset is stored in one file,
and the ``read_func`` take the path as the first parameter.
