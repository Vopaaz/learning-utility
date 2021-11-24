Changelog
==============

v0.1.9
^^^^^^^^^^^^^^^^^^^^^^^
* Fix the bug that the Exceptions in the `InlineCheckpoint` still results in the `produce` variables to be cached

v0.1.8
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Fix a bug when the line number cannot be correctly identified in jupyter notebook

v0.1.7
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Fix a corner case, where the numpy array created from `pd.DataFrame.to_numpy()` cannot be properly hashed.


v0.1.6
^^^^^^^^^^^^^^^^^^^
* Support pandas DataFrame with initially un-hashable elements as a parameter.

v0.1.5
^^^^^^^^^^^^^^^^^^
* Bug fixes
* Now the file name of ``Autosaver.save`` is optional, will use ``datetime.datetime.now().strftime(r"%m%d-%H%M%S") + ".csv"`` if left empty
* Add ``__recompute__`` functionality for ``checkpoint``

v0.1.4
^^^^^^^^^^^^^^^^
* Fix requirements.txt for Windows environment

v0.1.3
^^^^^^^^^^^^^^^^^^^^^^^^^^
* Add support for two ``AutoSaver`` cases
    * Fix: when a column header in the example file is empty, the output csv will no longer have an ``Unnamed: 0`` as header.
    * Feature: now it can handle ruleless indexes, as long as the example csv and the to-submit object has the same number of rows

v0.1.2
^^^^^^^^^^^^^^^^^
* Fix dependencies in requirements.txt and setup.py
* Use better way to hash a pandas object

v0.1.1
^^^^^^^^^^^^^^^^^^
* Fix changelog in the documentation (v0.0.1 -> v0.1.0)
* Fix fields in the setup.py
* More badges in the readme and documentation
* No code change


v0.1.0
^^^^^^^^^^^^
* Initialize the ``checkpoints`` module
    * ``InlineCheckpoint``
    * ``checkpoint``
* Initialize the ``dataIO`` module
    * ``AutoSaver``
    * ``DataReader``
