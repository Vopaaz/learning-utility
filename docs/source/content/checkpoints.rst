checkpoints: Caching Intermediate Results
=============================================

There are usually some intermediate results when doing machine learning tasks.
For example, the data after preprocessing.
This module is useful for caching them on the disk, and skip re-calculation when
is called afterwards.


.. contents::

.. py:module:: Lutil.checkpoints

InlineCheckpoint, the Context Manager
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

``InlineCheckpoint`` is a context manager.
It caches the output produced within the with-statement.
When the script is executed later with the same condition,
the cache is retrieved thus avoiding re-computation.

It is fully compatible with the jupyter notebook, and is often useful when using
it for machine learning.

.. py:class:: InlineCheckpoint(*, watch, produce)


    :param watch: List of names of variables used to identify a computing context
    :type watch: list or tuple
    :param produce: List of names of variables whose values are generated within the with-statement
    :type produce: list or tuple

Basic Example
^^^^^^^^^^^^^^^^

We have provided the simplest example in
`the welcome page <../index.html#cache-intermediate-results>`_,
here is a more practical one.

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
But the ``produce`` will be retrieved from cache, you will get::

    (10000, 20)

Condition of Re-computation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the variables or objects you watched have changed, for example,
the data or the parameter for the sklearn transformer,
code in the with-statement will be executed to retrieve the correct result.

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

Thus, please make sure that everything affecting the computation result is included
in the ``watch``.

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

checkpoint, the Decorator
"""""""""""""""""""""""""""""""""

``checkpoint`` is a decorator which cache the return value of a function or method on the disk.
When the function is called later with the same condition,
retrieve the cached value and return, avoiding re-computation.

.. py:decorator:: checkpoint
.. py:decorator:: checkpoint(ignore=[])

    :param ignore: List of names of variables ignored when identifying a computing context
    :type ignore: list or tuple


Basic Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose you have such a .py file:

.. code-block:: python

    from Lutil.checkpoints import checkpoint

    @checkpoint
    def foo(a, b):
        print("Heavy computation.")
        return a + b

    print(foo(1, 2))
    print(foo(1, 2))

Run this script, you will get::

    Heavy computation.
    3
    3

In the second call of ``foo``, the computation is skipped, and the return
value is retrieved from cache.

In machine learning tasks, the parameters are often pd.DataFrame or np.ndarray,
``checkpoint`` works well on them.

Condition of Re-computation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the parameter of the function have changed, the function will be
called again to retrieve the correct result.

In the previous example, add a new function call

.. code-block:: python

    print(foo(1, 3))

You will get::

    Heavy computation.
    4

If the code of the function have changed, re-computation takes place as well.

In the previous example, change the function definition from
``return a + b`` to ``return a - b``, and call ``print(foo(1, 2))`` again,
you will get::

    Heavy computation.
    -1



Ignore Some Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, ``checkpoint`` monitors all the parameters of the decorated function.
However, the ``ignore`` parameter can be used if some of them are not contributing to the return value.

.. code-block:: python

    @checkpoint(ignore=["useless"])
    def bar(a, useless):
        print("Runned.")
        return a + 1

    print(bar(1, True))
    print(bar(1, False))

Althought the value of ``useless`` have changed, there will be no re-computation.
You will get::

    Runned.
    2
    2


Complex Object as a Parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If some parameters of the decorated function are neither
basic data types nor pd.DataFrame/np.ndarray,
a warning will be raised. It is not recommended to do so.

.. code-block:: python

    @checkpoint
    def func(foo):
        return foo

    class Foo: pass
    f = Foo()
    f.foo = Foo()

    func(foo)

You will get:

.. code-block:: text

    ComplexParamsIdentifyWarning: A complicated object is an attribute of <__main__.Foo object at 0x00000224A1575358>,
    it may cause mistake when detecting whether there is checkpoint for this call.



See Also
^^^^^^^^^^^^^^^^^

`joblib.Memory <https://joblib.readthedocs.io/en/latest/memory.html#memory>`_ is similar
to our ``checkpoint`` decorator.
It is more powerful, while ours is more concise.

However, ``joblib`` is not providing anything similar to our ``InlineCheckpoint``,
while this is often necessary in some jupyter notebook based solutions.
This is also the motivation of this module.

Another important difference is that, if the code of the function changes,
``joblib.Memory`` only caches the result of the latest function version.

.. code-block:: python

    from joblib import Memory
    memory = Memory("dir", verbose=0)

    @memory.cache
    def f(x):
        print('Running.')
        return x

    f(1)

Run this, you get::

    Running.

If you change ``print('Running.')`` to ``print('Running again.)'``, you will get::

    Running again.

Now, if you change it back to ``print('Running')``, it will not retrieve
the result in the first run. Instead, the computation happens again::

    Running.

However, if you are using our ``checkpoint``.

.. code-block:: python

    from Lutil.checkpoints import checkpoint

    @checkpoint
    def f(x):
        print('Running.')
        return x

Do the similar thing, and in the third run, the computation will be skipped.
The result in the first run will be retrieved.
