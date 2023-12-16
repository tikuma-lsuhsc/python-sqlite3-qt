"""
The sqlite3 extension module provides most of the DB-API 2.0 (PEP 249) compliant
interface to the SQLite library via PyQt/PySide QtSql module.

To use the module, start by creating a database Connection object:

    import sqlite3_qt as sqlite3
    cx = sqlite3.connect("test.db")  # test.db will be created or opened

The special path name ":memory:" can be provided to connect to a transient
in-memory database:

    cx = sqlite3.connect(":memory:")  # connect to a database in RAM

Once a connection has been established, create a Cursor object and call
its execute() method to perform SQL queries:

    cu = cx.cursor()

    # create a table
    cu.execute("create table lang(name, first_appeared)")

    # insert values into a table
    cu.execute("insert into lang values (?, ?)", ("C", 1972))

    # execute a query and iterate over the result
    for row in cu.execute("select * from lang"):
        print(row)

    cx.close()
"""

__version__ = '0.1.0'

from .dbapi2 import *



# bpo-42264: OptimizedUnicode was deprecated in Python 3.10.  It's scheduled
# for removal in Python 3.12.
def __getattr__(name):
    if name == "OptimizedUnicode":
        import warnings
        msg = ("""
            OptimizedUnicode is deprecated and will be removed in Python 3.12.
            Since Python 3.3 it has simply been an alias for 'str'.
        """)
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        return str
    raise AttributeError(f"module 'sqlite3' has no attribute '{name}'")
