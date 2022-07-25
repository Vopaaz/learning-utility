Unmaintained
===================================================

**This project is unmaintained and the checkpoint functionality has been migrated to the** `**checkpointing** <https://github.com/Vopaaz/checkpointing>`_ **project.**


Assist small-scale machine learning.
===================================================

learning-utility is a package of utilities for small-scale machine learning tasks with scikit-learn.

.. image:: https://www.travis-ci.org/Vopaaz/learning-utility.svg?branch=master
    :target: https://www.travis-ci.org/Vopaaz/learning-utility

.. image:: https://codecov.io/gh/Vopaaz/learning-utility/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Vopaaz/learning-utility

.. image:: https://img.shields.io/pypi/pyversions/Lutil
    :alt: PyPI - Python Version

.. image:: https://pepy.tech/badge/lutil
    :target: https://pepy.tech/project/lutil
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/Lutil
    :alt: PyPI

Installation
""""""""""""""""

.. code-block:: bash

    pip install Lutil


Key Features
""""""""""""""""""""


Cache Intermediate Results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``InlineCheckpoint`` can cache the computation result in the first call.
Since then, if nothing has changed, it retrieves the cache and skips computation.

Suppose you have such a .py file.

.. code-block:: python

    from Lutil.checkpoints import InlineCheckpoint

    a, b = 1, 2
    with InlineCheckpoint(watch=["a", "b"], produce=["c"]):
       print("Heavy computation.")
       c = a + b

    print(c)

Run the script, you will get::

    Heavy computation.
    3

Run this script again, the with-statement will be skipped. You will get::

    3

Once a value among ``watch`` changes or the code inside the with-statement changes,
re-calculation takes place to ensure the correct output.

Please check out the details for `InlineCheckpoint <./content/checkpoints.html#inlinecheckpoint-the-context-manager>`_.

Save Prediction Result According to the Given Format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lots of machine learning competitions require a .csv file in a given format.
Most of them provide an example file.

In example.csv:

.. code-block:: text

    id, pred
    1, 0.25
    2, 0.45
    3, 0.56

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

    id, pred
    1, 0.2
    2, 0.4
    3, 0.1
    4, 0.5

It also works if the ``result`` is a pandas DataFrame, Series, 2-dim numpy array, etc.
Also, the encoding, seperator, header, index of the example.csv will all be recognized.

Please check out the details for `AutoSaver <./content/dataIO.html#autosaver-auto-format-and-save-prediction-results>`_.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   content/checkpoints.rst
   content/dataIO.rst

   content/changelog.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
