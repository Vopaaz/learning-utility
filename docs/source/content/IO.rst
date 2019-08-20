IO Module: Read Data, Cache/Save Result
=============================================

.. contents::


.. py:module:: Lutil.IO

InlineCheckpoint
""""""""""""""""""""""

.. py:class:: InlineCheckpoint(*, watch, produce, [_id="default"])

    A context manager. Cache the output produced within the with-statement.
    When is executed later with the same condition,
    retrieve the cache and avoid re-computation.

    :param watch: List of variables used to identify a computing context
    :type watch: list or tuple
    :param produce: List of variables whose values are generated within the with-statement
    :type produce: list or tuple
    :param str _id: Indentifier for very special case

    We have provided the most basic example in
    `the welcome page <../index.html#cache-intermediate-results>`_,
    here is a more practical one:

    Suppose you have such a .py file.

    .. code-block:: python

        from Lutil.IO import InlineCheckpoint

        import numpy as np
        from sklearn.decomposition import PCA

        np.random.seed(0)                   # If random seed is not set, data will change every time
        data = np.random.randn(10000, 1000) # Simulate a large dataset
        pca = PCA(20)                       # A typical scikit-learn transformer

        with InlineCheckpoint(watch=["data", "pca"], produce=["data_t"]):
            data_t = pca.fit_transform(data)
            print("A thousand years later.")

        print(data_t.shape)

    Run the script, you will get::

        A thousand years later.
        (10000, 20)

    Run this script again, the with-statement will be skipped.
    But the 'produce' will be retrieved from cache, you will get::

        (10000, 20)

    If you the values watched has changed, for example,
    the data or the parameter for the sklearn transformer,
    it re-compute the code in with-statement to retrieve the correct result.

    For example, if you replace ``pca = PCA(20)`` with

    .. code-block:: python

        pca = PCA(50)

    Run the script again, you will get::

        A thousand years later.
        (10000, 50)

    It also monitors whether the code in the with-statement has changed,
    for example, if you replace ``data_t = pca.fit_transform(data)`` with

    .. code-block:: python

        data_t = data

    The with-statement is executed::

        A thousand years later.
        (10000, 1000)

    The ``watch`` and ``produce`` can also be attributes of some object,
    using the ``.`` syntax.

    This works:

    .. code-block:: python

        class Foo: pass

        f = Foo()
        f.a = 1

        with InlineCheckpoint(watch=["f.a"], produce=["f.b"]):
            f.b = f.a
        print(f.b)

    However, the slice syntax is not yet supported. This will cause error:

    .. code-block:: python

        d = {'a':1}

        with InlineCheckpoint(watch=["d['a']"], produce=["d['b']"]):
            d['b'] = d['a']

    .. caution::

        Because of some limitation of python magic we used to skip the code block
        and load the cached data,
        InlineCheckpoint **to produce variables** is **not supported within a function or method**.

        This will not work!

        .. code-block:: python

            def func(a):
                with InlineCheckpoint(watch=["a"], produce=["b"]):
                    b = a
                return b

    However, producing attributes of an object works well:

    .. code-block:: python

        def func(a):
            f = Foo()
            with InlineCheckpoint(watch=["a"], produce=["f.b"]):
                f.b = a
            return f.b

    Nevertheless, `checkpoint as a decorator <#function-decorator-checkpoint>`_ is recommended
    for a function. Besides, if you use this, the return statement should not be included
    in the with-statement.



Function Decorator: checkpoint
"""""""""""""""""""""""""""""""""

.. py:decorator:: checkpoint
.. py:decorator:: checkpoint(ignore=[])

    Cache the return value of a function or method.
    When is called later with the same condition, retrieve the cache and skip the with-statement.





.. py:class:: AutoSaver(save_dir="", example_path=None, **default_kwargs)

.. py:class:: DataReader(train_path=None, test_path=None, val_path=None, *, _id="default", read_func=None, **read_kwargs)


