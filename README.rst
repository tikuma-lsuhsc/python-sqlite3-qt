.. meta::
   :author: Takeshi Ikuma
   :title: Python SQLite3-Qt - Drop-in replacement for sqlite3 using Qt's QtSql module
   :description: Seemless switching between Python's built-in sqlite3 module with PyQt QtSql module

|pypi| |pypi-status| |pypi-pyvers| |github-license| 

.. 
   |github-status|

.. |pypi| image:: https://img.shields.io/pypi/v/sqlite3-qt
  :alt: PyPI
.. |pypi-status| image:: https://img.shields.io/pypi/status/sqlite3-qt
  :alt: PyPI - Status
.. |pypi-pyvers| image:: https://img.shields.io/pypi/pyversions/sqlite3-qt
  :alt: PyPI - Python Version
.. |github-license| image:: https://img.shields.io/github/license/tikuma-lsuhsc/python-sqlite3-qt
  :alt: GitHub License
.. |github-status| image:: https://img.shields.io/github/workflow/status/python-sqlite3-qt/python-sqlite3-qt/test_n_pub
  :alt: GitHub Workflow Status

About SQLite3-Qt
~~~~~~~~~~~~~~~~

A drop-in module for `Python's sqlite3 built-in module`_, providing basic 
functionality via `Qt SQL module`_. The goal is to enable the creation of a SQL backend module 
which can support both script and UI frontends.

.. _Python's sqlite3 built-in module: https://docs.python.org/3/library/sqlite3.html
.. _Qt SQL module: https://doc.qt.io/qt-6/qtsql-index.html

Installation
~~~~~~~~~~~~

Install using pip::

   pip install sqlite3-qt

Features
~~~~~~~~

- Supports the basic database operations including binding values. (See below for supported ``sqlite3`` classes and functions.)

- API to mimic built-in `sqlite3` module to enable easy swapping:

  .. code-block:: python
    
      # import sqlite3              # default import
      import sqlite3_qt as sqlite3  # drop-in replacement without any change in the code

      ...

- Underlying Qt Database connection name is auto-generated and transparent

.. |QSqlDatabase| replace:: ``QSqlDatabase``
.. |QSqlQuery| replace:: ``QSqlQuery``
.. |PySide2| replace:: ``PySide2``

- Access Qt's QSqlDatabase_ name and QSqlQuery_ objects

  .. code-block:: python

    sqlite3_qt.Connection.qt_name # to get the QSqlDatabase name
    sqlite3_qt.Cursor.qt_query # to access the underlying QSqlQuery object

.. role:: strike
    :class: strike


- Auto-detect ``PyQt6`` / ``PySide6`` / ``PyQt5`` / :strike:`PySide2` (`PySide2` fails the Github CI test)
   
.. _QSqlDatabase: https://doc.qt.io/qt-6/qsqldatabase.html
.. _QSqlQuery: https://doc.qt.io/qt-6/qsqlquery.html
.. _Qt SQLite plugin: https://doc.qt.io/qt-6/sql-driver.html#qsqlite

Compatibility Table
~~~~~~~~~~~~~~~~~~~

Unfortunately, not all features of `Python's sqlite3 built-in module`_ can be supported by `Qt SQL module`_. 
The table below summarizes which ``sqlite3`` functions/classes are currently supported.

.. |_| unicode:: 0xA0 
   :trim:

========================================  ============
``sqlite3`` functions and classes         Supported?
========================================  ============
``sqlite3.connect(``                      Partially
|_| |_| ``database,``                     Yes
|_| |_| ``timeout,``                      Yes
|_| |_| ``detect_types,``                 No
|_| |_| ``isolation_level,``              No
|_| |_| ``check_same_thread,``            No
|_| |_| ``factory,``                      Yes
|_| |_| ``cached_statements,``            No
|_| |_| ``uri,``                          Yes
|_| |_| ``autocommit)``                   No
``class sqlite3.Connection``              Yes
|_| |_| ``cursor()``                      Yes
|_| |_| ``blobopen()``                    No
|_| |_| ``commit()``                      Yes 
|_| |_| ``rollback()``                    Yes
|_| |_| ``close()``                       Yes
|_| |_| ``execute()``                     Yes
|_| |_| ``executemany()``                 Yes
|_| |_| ``executescript()``               Yes
|_| |_| ``create_function()``             No
|_| |_| ``create_aggregate()``            No
|_| |_| ``create_window_function()``      No
|_| |_| ``create_collation()``            No
|_| |_| ``interrupt()``                   No
|_| |_| ``set_authorizer()``              No
|_| |_| ``set_progress_handler()``        No
|_| |_| ``set_trace_callback()``          No
|_| |_| ``enable_load_extension()``       No
|_| |_| ``load_extension()``              No
|_| |_| ``iterdump()``                    No
|_| |_| ``backup()``                      No
|_| |_| ``getlimit()``                    No
|_| |_| ``setlimit()``                    No
|_| |_| ``getconfig()``                   No
|_| |_| ``setconfig()``                   No
|_| |_| ``serialize()``                   No
|_| |_| ``deserialize()``                 No
|_| |_| ``autocommit``                    ??
|_| |_| ``in_transaction``                No
|_| |_| ``isolation_level``               No
|_| |_| ``row_factory``                   Yes
|_| |_| ``text_factory``                  Yes
|_| |_| ``total_changes``                 No

``class sqlite3.Cursor``                  Yes
|_| |_| ``execute()``                     Yes
|_| |_| ``executemany()``                 Yes
|_| |_| ``executescript()``               Yes
|_| |_| ``fetchone()``                    Yes
|_| |_| ``fetchmany()``                   Yes
|_| |_| ``fetchall()``                    Yes
|_| |_| ``close()``                       Yes
|_| |_| ``setinputsizes()``               No
|_| |_| ``setoutputsize()``               No
|_| |_| ``arraysize``                     Yes
|_| |_| ``connection``                    Yes
|_| |_| ``description``                   Yes
|_| |_| ``lastrowid``                     Yes
|_| |_| ``rowcount``                      Yes
|_| |_| ``row_factory``                   Yes

``class sqlite3.Row``                     Yes
|_| |_| ``keys()``                        Yes
``class sqlite3.Blob``                    No

``sqlite3.complete_statement()``          No
``sqlite3.enable_callback_tracebacks()``  No
``sqlite3.register_adapter()``            No (TODO)
``sqlite3.register_converter()``          No (TODO)
``sqlite3.apilevel``                      No
``sqlite3.paramstyle``                    No
``sqlite3.sqlite_version``                Yes
``sqlite3.sqlite_version_info``           Yes
``sqlite3.threadsafety``                  No
``sqlite3.version``                       Yes
``sqlite3.version_info``                  Yes
========================================  ============
