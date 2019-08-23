checkpoints: Auto-Caching
=============================================

.. contents::

.. py:module:: Lutil.checkpoints

InlineCheckpoint, the context manager
""""""""""""""""""""""""""""""""""

.. py:class:: InlineCheckpoint(*, watch, produce)

    A context manager. Cache the output produced within the with-statement.
    When is executed later with the same condition,
    retrieve the cache and avoid re-computation.

    :param watch: List of names of variables used to identify a computing context
    :type watch: list or tuple
    :param produce: List of names of variables whose values are generated within the with-statement
    :type produce: list or tuple

Basic Example
^^^^^^^^^^^^^^^^

    We have provided the simplest example in
    `the welcome page <../index.html#cache-intermediate-results>`_,
    here is a more practical one:

    Suppose you have such a .py file.

    .. code-block:: python

        from Lutil.checkpoints import InlineCheckpoint

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

Condition of Re-computation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    If the values you watched has changed, for example,
    the data or the parameter for the sklearn transformer,
    it re-compute the code in with-statement to retrieve the correct result.

    For instance, if you replace ``pca = PCA(20)`` with ``pca = PCA(50)`` and
    run the script again, you will get::

        A thousand years later.
        (10000, 50)

    The code in the with-statement is also monitored to detect whether the condition
    has changed.

    For example, if you replace ``data_t = pca.fit_transform(data)`` with ``data_t = data``
    The re-computation will be executed::

        A thousand years later.
        (10000, 1000)


Format of Watch and Produce
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Basically, the items in the ``watch``/``produce`` list shoule be valid
    variable names in Python.

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

    Nevertheless, `checkpoint as a decorator <#checkpoint-the-decorator>`_ is recommended
    for a function. Besides, if you use this, the return statement should not be included
    in the with-statement.

Watching a Complex Object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    If the object you are watching has some attributes, which are neither basic data types
    nor pd.DataFrame/np.ndarray, a warning will be raised.
    It is not recommended to do so. Instead, explicitly watch those attributes which affects
    the computation, using the ``.`` syntax.

    .. code-block:: python

        class Bar: pass
        f = Foo()
        f.bar = Bar()

        with InlineCheckpoint(watch=["f"], produce=["f.a"]):
            f.a = 1

    will give you:

    .. code-block:: text

        ComplexParamsIdentifyWarning: A complicated object is an attribute of <__main__.Foo object at 0x000001CE66E897B8>,
        it may cause mistake when detecting whether there is checkpoint for this call.

checkpoint, the decorator
"""""""""""""""""""""""""""""""""

.. py:decorator:: checkpoint
.. py:decorator:: checkpoint(ignore=[])

    Cache the return value of a function or method.
    When is called later with the same condition, retrieve the cache and skip the with-statement.



