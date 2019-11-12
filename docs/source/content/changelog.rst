Changelog
==============

v0.1.5
^^^^^^^^^^^^^^^^^^
* Bug fixes

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
