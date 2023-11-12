from __future__ import annotations

from sqlite3.dbapi2 import *
from sqlite3.dbapi2 import connect as _connect
from os import PathLike
from functools import lru_cache

from .qt_compat import QtSql, QT_API, QtCore

from typing_extensions import (
    Self,
    Any,
    Callable,
    Iterable,
    Optional,
    Literal,
    Generator,
    Tuple,
    List,
    Iterator,
    Sequence,
    Mapping,
)

# version_info: tuple[int, int, int]
# version: str

# # Can take or return anything depending on what's in the registry.
# @overload
# def adapt(obj: Any, proto: Any) -> Any: ...
# @overload
# def adapt(obj: Any, proto: Any, alt: _T) -> Any  _T: ...
# def complete_statement(statement: str) -> bool: ...


class Cursor:
    ...


def getattr(name):
    if name in ("sqlite_version_info"):
        return _sqlite_version(info=True)
    elif name in ("sqlite_version"):
        return _sqlite_version()
    raise AttributeError(f"module '{name}' has no attribute '{name}'")


@lru_cache(maxsize=None)
def _sqlite_version(info: bool = False):
    def query():
        con = QtSql.QSqlDatabase.addDatabase("QSQLITE", "ver")
        con.setDatabaseName(":memory:")
        if not con.open():
            raise Exception("failed to open")
        try:
            query = QtSql.QSqlQuery("SELECT sqlite_version()", con)
            if not query.first():
                raise Exception("sqlite_version() failed to run")
            return query.value(0)
        finally:
            con.close()

    ver = query()
    QtSql.QSqlDatabase.removeDatabase("ver")

    if info:
        return tuple(int(s) for s in ver.split("."))


def connect(database: PathLike, *args, **kwargs) -> Connection:
    """Open a connection to an SQLite database.

    :param database: The path to the database file to be opened. You can pass ":memory:" to create an SQLite database existing only in memory, and open a connection to it.
    :type database: PathLike
    :param timeout: How many seconds the connection should wait before raising an OperationalError when a table is locked. If another connection opens a transaction to modify a table, that table will be locked until the transaction is committed. Defaults to 5 seconds
    :type timeout: float, optional
    :param detect_types: Control whether and how data types not natively supported by SQLite are looked up to be converted to Python types, using the converters registered with register_converter(). Set it to any combination (using , bitwise or) of PARSE_DECLTYPES and PARSE_COLNAMES to enable this. Column names takes precedence over declared types if both flags are set. Types cannot be detected for generated fields (for example max(data)), even when the detect_types parameter is set; str will be returned instead. By default (0), type detection is disabled
    :type detect_types: int, optional
    :param isolation_level: Control legacy transaction handling behaviour. See Connection.isolation_level and Transaction control via the isolation_level attribute for more information. Can be "DEFERRED" (default), "EXCLUSIVE" or "IMMEDIATE"; or None to disable opening transactions implicitly. Has no effect unless Connection.autocommit is set to LEGACY_TRANSACTION_CONTROL (the default).
    :type isolation_level: str  None, optional
    :param check_same_thread: If True (default), ProgrammingError will be raised if the database connection is used by a thread other than the one that created it. If False, the connection may be accessed in multiple threads; write operations may need to be serialized by the user to avoid data corruption. See threadsafety for more information.
    :type check_same_thread: bool, optional
    :param factory: A custom subclass of Connection to create the connection with, if not the default Connection class.
    :type factory: Connection | None, optional
    :param cached_statements: The number of statements that sqlite3 should internally cache for this connection, to avoid parsing overhead. By default, 128 statements.
    :type cached_statements: int, optional
    :param uri: If set to True, database is interpreted as a URI with a file path and an optional query string. The scheme part must be "file:", and the path can be relative or absolute. The query string allows passing parameters to SQLite, enabling various How to work with SQLite URIs.
    :type uri: bool, optional
    :return: opened database connection
    :rtype: Connection
    """

    if "factory" not in kwargs and len(args) < 5:
        kwargs["factory"] = Connection

    return _connect(database, *args, **kwargs)


def enable_callback_tracebacks(enable: bool):
    """Enable or disable callback tracebacks. Not supported."""
    raise NotImplementedError()


class Blob:
    def __init__(self):
        raise NotImplementedError()

    # def close(self):
    #     ...

    # def read(self, length: int = -1) -> bytes:
    #     ...

    # def write(self, data: ReadableBuffer):
    #     ...

    # def tell(self) -> int:
    #     ...

    # # whence must be one of os.SEEK_SET, os.SEEK_CUR, os.SEEK_END
    # def seek(self, offset: int, origin: int = 0):
    #     ...

    # def __len__(self) -> int:
    #     ...

    # def __enter__(self) -> Self:
    #     ...

    # def __exit__(self, type: object, val: object, tb: object) -> Literal[False]:
    #     ...

    # def __getitem__(self, key: SupportsIndex | slice) -> int:
    #     ...

    # def __setitem__(self, key: SupportsIndex | slice, value: int):
    #     ...


class Row:
    def __init__(self, cursor: Cursor, row: Tuple[Any]):
        self.qt_record = cursor.qt_query.record()

    def __keys__(self) -> List[str]:
        r = self.qt_record
        return [r.fieldName(k) for k in range(r.count())]

    def __getitem__(self, key: int | str | slice) -> Any:
        r = self.qt_record
        return [r.value(i) for i in key] if isinstance(key, slice) else r.value(key)

    def __hash__(self) -> int:
        # PyObject_Hash(self->description) ^ PyObject_Hash(self->data)
        ...

    def __iter__(self) -> Iterator[Any]:
        return self.keys()

    def __len__(self) -> int:
        return self.qt_record.count()

    # These return NotImplemented for anything that is not a Row.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Row):
            return NotImplemented
        return all(key in other and self[key] == other[key] for key in self.keys())

    def __ge__(self, other: object) -> bool:
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        return NotImplemented

    def __le__(self, other: object) -> bool:
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        return NotImplemented

    def _ne_(self, other: object) -> bool:
        if not isinstance(other, Row):
            return NotImplemented
        return any(key not in other or self[key] != other[key] for key in self.keys())


class Cursor(Iterator):
    def __init__(self, conn: Connection):
        self._conn = conn
        self.qt_query = QtSql.QSqlQuery(conn.qt_database)
        self.row_factory: None | Callable = conn.row_factory
        self.arraysize: int = 1

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Any:
        out = self.fetchone()
        if out is None:
            raise StopIteration()
        return out

    @staticmethod
    def _flag(v):
        flag = QtSql.QSql.ParamTypeFlag.InOut
        try:
            v = QtCore.QByteArray(bytes(memoryview(v)))
            flag = flag | QtSql.QSql.ParamTypeFlag.Binary
        finally:
            return v, flag

    @staticmethod
    def _sflag(seq):
        flag = QtSql.QSql.ParamTypeFlag.InOut
        try:
            seq = [QtCore.QByteArray(bytes(memoryview(v))) for v in seq]
            flag = flag | QtSql.QSql.ParamTypeFlag.Binary
        finally:
            return seq, flag

    def execute(
        self, sql: str, parameters: Optional[Sequence | Mapping] = None
    ) -> Self:
        """Execute SQL a single SQL statement, optionally binding Python values using placeholders.

        :param sql: A single SQL statement.
        :type sql: str
        :param parameters: Python values to bind to placeholders in sql. A dict if named
                           placeholders are used. A sequence if unnamed placeholders are used.
        :type parameters: Sequence | Mapping, optional
        :raises ProgrammingError: If sql contains more than one SQL statement.
        :return: cursor
        :rtype: Self
        """
        q = self.qt_query
        if not q.prepare(sql):
            raise ProgrammingError(q.lastError().text())
        if isinstance(parameters, Sequence):
            for i, v in enumerate(parameters):
                q.bindValue(i, *self._flag(v))  # TODO add adapter
        elif isinstance(parameters, Mapping):
            for k, v in parameters.items():
                q.bindValue(f":{k}", *self._flag(v))  # TODO add adapter
        if not q.exec():
            raise DatabaseError(q.lastError().text())

        return self

    def executemany(
        self,
        sql: str,
        seq_of_parameters: Optional[Iterable[Sequence | Mapping]] = None,
    ) -> Self:
        """For every item in parameters, repeatedly execute the parameterized DML SQL statement sql.

        Uses the same implicit transaction handling as execute().

        :param sql: A single SQL DML statement.
        :type sql: str
        :param seq_of_parameters: An iterable of parameters to bind with the placeholders in sql.
        :type seq_of_parameters: Optional[Iterable[Sequence  |  Mapping]], optional
        :raises ProgrammingError: If sql contains more than one SQL statement, or is not a DML.
        :return: cursor
        :rtype: Self
        """
        q = self.qt_query
        if not q.prepare(sql):
            # TODO - check Programming or Database error
            raise ProgrammingError(q.lastError().text())

        if len(seq_of_parameters):
            if isinstance(seq_of_parameters[0], Sequence):
                for i, v in enumerate(list(t) for t in zip(*seq_of_parameters)):
                    q.bindValue(i, *self._sflag(v))  # TODO add adapter
            elif isinstance(seq_of_parameters[0], Mapping):
                for k in seq_of_parameters[0].keys():
                    q.bindValue(
                        f":{k}",
                        *self._sflag([v[k] for v in seq_of_parameters]),
                    )
                    # TODO add adapter
        if not q.execBatch():
            raise DatabaseError(q.lastError().text())

        return self

    def executescript(self, sql_script: str) -> Cursor:
        """Execute the SQL statements in sql_script.

        If the autocommit is LEGACY_TRANSACTION_CONTROL and there is a pending transaction, an
        implicit COMMIT statement is executed first. No other implicit transaction control is
        performed; any transaction control must be added to sql_script.

        :param sql_script: SQL script
        :type sql_script: str
        :raises DatabaseError: _description_
        :return: _description_
        :rtype: Cursor
        """
        iter_lines = (readLine for readLine in sql_script.splitlines())
        q = self.qt_query
        try:
            while True:
                lines = []
                finished = False

                while not finished:
                    readLine = next(iter_lines)
                    cleanedLine = readLine.strip()
                    # remove comments at end of line
                    cleanedLine = cleanedLine.split("--", 1)[0]

                    # remove lines with only comment, and DROP lines
                    if not (
                        cleanedLine.startsWith("--") or cleanedLine.startsWith("DROP")
                    ) and len(cleanedLine):
                        lines.append(cleanedLine)

                    if cleanedLine.endsWith(";"):
                        break

                    if cleanedLine.startsWith("COMMIT"):
                        finished = True

                line = " ".join(lines)
                if len(line):
                    if not q.exec(line):
                        raise DatabaseError(q.lastError().text())

        except StopIteration:
            pass

        return self

    def _fetch_tuple(self):
        q = self.qt_query
        n = q.record().count()
        return tuple(q.value(i) for i in range(n))

    def fetchone(self) -> Any:
        """If row_factory is None, return the next row query result set as a tuple. Else, pass it to
        the row factory and return its result. Return None if no more data is available.
        """
        if self.qt_query.next():
            return self._fetch_tuple()

    def fetchmany(self, size: int | None = 0) -> List[Any]:
        """Return the next set of rows of a query result as a list.

        Return an empty list if no more rows are available.

        Note there are performance considerations involved with the size parameter. For optimal
        performance, it is usually best to use the arraysize attribute. If the size parameter is
        used, then it is best for it to retain the same value from one fetchmany() call to the next.

        :param size: The number of rows to fetch per call is specified by the size parameter. If
                     size is not given, arraysize determines the number of rows to be fetched. If
                     fewer than size rows are available, as many rows as are available are returned.
                     Default is 1
        :type size: int | None, optional
        :return: fetched rows
        :rtype: list[Any]
        """

        if size <= 0:
            size = self.arraysize

        q = self.qt_query

        def fetch():
            i = 0
            while q.next() and i < size:
                yield self._fetch_tuple()
                i += 1

        return [row for row in fetch()]

    def fetchall(self) -> List[Any]:
        """Return all (remaining) rows of a query result as a list.

        Return an empty list if no rows are available.
        """
        q = self.qt_query

        def fetch():
            while q.next():
                yield self._fetch_tuple()

        return [row for row in fetch()]

    def close(self):
        """Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; a ProgrammingError exception will be
        raised if any operation is attempted with the cursor.

        """

        self.qt_query.finish()

    @property
    def connection(self) -> Connection:
        """Read-only attribute that provides the SQLite database Connection belonging to the cursor.

        A Cursor object created by calling con.cursor() will have a connection attribute that refers to con
        """
        return self._conn

    def setinputsizes(self, sizes):
        raise NotImplementedError()

    def setoutputsize(self, size, column):
        raise NotImplementedError()

    @property
    def description(
        self,
    ) -> Tuple[Tuple[str, None, None, None, None, None, None], ...] | Any:
        """Read-only attribute that provides the column names of the last query.

        To remain compatible with the Python DB API, it returns a 7-tuple for each column where the
        last six items of each tuple are None. It is set for SELECT statements without any matching
        rows as well."""

        q = self.qt_query
        i = q.at()
        if i in (QtSql.QSql.BeforeFirstRow, QtSql.QSql.AfterLastRow) and not q.last():
            raise DatabaseError("No rows returned by the last query")

        r = q.record()
        res = tuple(
            (r.fieldName(k), None, None, None, None, None, None)
            for k in range(r.count())
        )

        if i == QtSql.QSql.BeforeFirstRow:
            q.seek(-1)
        elif i == QtSql.QSql.AfterLastRow:
            q.seek(1, True)

        return res

    @property
    def lastrowid(self) -> int | None:
        """Read-only attribute that provides the row id of the last inserted row.

        It is only updated after successful INSERT or REPLACE statements using the execute() method.
        For other statements, after executemany() or executescript(), or if the insertion failed,
        the value of lastrowid is left unchanged. The initial value of lastrowid is None.
        """

        # TODO - create a private property to store these results after execution
        return self.qt_query.lastInsertId()

    @property
    def rowcount(self) -> int | None:
        """Read-only attribute that provides the number of modified rows for INSERT, UPDATE, DELETE,
        and REPLACE statements; is -1 for other statements, including CTE queries.

        It is only updated by the execute() and executemany() methods, after the statement has run
        to completion. This means that any resulting rows must be fetched in order for rowcount to
        be updated.
        """
        # TODO - create a private property to store these results after execution
        return self.qt_query.size()


class Connection:
    DataError = DataError
    DatabaseError = DatabaseError
    Error = Error
    IntegrityError = IntegrityError
    InterfaceError = InterfaceError
    InternalError = InternalError
    NotSupportedError = NotSupportedError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    Warning = Warning

    row_factory: Any = None
    """The initial row_factory for Cursor objects created from this connection. Assigning to this attribute does not affect the row_factory of existing cursors belonging to this connection, only new ones. Is None by default, meaning each row is returned as a tuple."""

    text_factory: Any = str
    """A callable that accepts a bytes parameter and returns a text representation of it. The callable is invoked for SQLite values with the TEXT data type. By default, this attribute is set to str."""

    @property
    def in_transaction(self) -> bool:
        """This read-only attribute corresponds to the low-level SQLite autocommit mode.

        True if a transaction is active (there are uncommitted changes), False otherwise.
        """
        raise NotImplementedError()

    @property
    def total_changes(self) -> int:
        """Return the total number of database rows that have been modified, inserted, or deleted since the database connection was opened."""
        raise NotImplementedError()

    @property
    def autocommit(self) -> int:
        """This attribute controls PEP 249-compliant transaction behaviour. autocommit has three allowed values:

            False: Select PEP 249-compliant transaction behaviour, implying that sqlite3 ensures a transaction is always open. Use commit() and rollback() to close transactions.

            This is the recommended value of autocommit.

            True: Use SQLite’s autocommit mode. commit() and rollback() have no effect in this mode.

            LEGACY_TRANSACTION_CONTROL: Pre-Python 3.12 (non-PEP 249-compliant) transaction control. See isolation_level for more details.

            This is currently the default value of autocommit.

        Changing autocommit to False will open a new transaction, and changing it to True will commit any pending transaction.
        """
        return True

    @autocommit.setter
    def autocommit(self, val: int):
        raise NotImplementedError()

    _cnt: int = 0

    def __init__(
        self,
        database: PathLike,
        timeout: float = 5.0,
        detect_types: int = 0,
        isolation_level: str | None = "DEFERRED",
        check_same_thread: bool = True,
        factory: type[Connection] | None = Connection,
        cached_statements: int = 128,
        uri: bool = False,
        *,
        autocommit: bool = True,
    ):
        self.isolation_level: str | None = (
            isolation_level  # one of '', 'DEFERRED', 'IMMEDIATE' or 'EXCLUSIVE'
        )

        name = f"con{self._cnt}"
        Connection._cnt += 1
        con = QtSql.QSqlDatabase.addDatabase("QSQLITE", name)
        con.setDatabaseName(str(database))

        if not (autocommit or con.transaction()):
            raise DatabaseError("QtSQL does not support transactions")

        opts = {
            "QSQLITE_BUSY_TIMEOUT": round(timeout * 1000),
            "QSQLITE_OPEN_URI": int(bool(uri)),
        }
        con.setConnectOptions(";".join([f"{k}={v}" for k, v in opts.items()]))

        if not con.open():
            raise DatabaseError(f"{database} failed to open.")

        self.qt_name = name

    @property
    def qt_database(self) -> QtSql.QSqlDatabase:
        return QtSql.QSqlDatabase.database(self.qt_name)

    def cursor(self, factory=Cursor) -> Cursor:
        """Create and return a Cursor object.

        The cursor method accepts a single optional parameter factory. If supplied, this must be a
        callable returning an instance of Cursor or its subclasses."""
        return factory(self)

    def blobopen(
        self,
        table: str,
        column: str,
        row: str,
        *,
        readonly: bool = False,
        name: str = "main",
    ) -> Blob:
        """Open a Blob handle to an existing BLOB.

        :param table: The name of the table where the blob is located.
        :type table: str
        :param column: The name of the column where the blob is located.
        :type column: str
        :param row: The name of the row where the blob is located.
        :type row: str
        :param readonly: Set to True if the blob should be opened without write permissions. Defaults to False.
        :type readonly: bool, optional
        :param name: The name of the database where the blob is located. Defaults to "main".
        :type name: str, optional
        :return: Blob handle
        :rtype: Blob
        """
        raise NotImplementedError()

    def commit(self):
        """Commit any pending transaction to the database.

        If autocommit is True, or there is no open transaction, this method does nothing.
        If autocommit is False, a new transaction is implicitly opened if a pending transaction was
        committed by this method."""

        if self.qt_database.transaction() and not self.qt_database.commit():
            raise DatabaseError(self.qt_database.lastError().text())

    def rollback(self):
        """Roll back to the start of any pending transaction.

        If autocommit is True, or there is no open transaction, this method does nothing. If
        autocommit is False, a new transaction is implicitly opened if a pending transaction was
        rolled back by this method."""

        if self.qt_database.transaction() and not self.qt_database.rollback():
            raise DatabaseError(self.qt_database.lastError().text())

    def close(self):
        """Close the database connection.

        If autocommit is False, any pending transaction is implicitly rolled back. If autocommit is
        True or LEGACY_TRANSACTION_CONTROL, no implicit transaction control is executed. Make sure
        to commit() before closing to avoid losing pending changes."""

        self.qt_database.close()

    def execute(self, sql: str, parameters: Any = None) -> Cursor:
        """Create a new Cursor object and call execute() on it with the given sql and parameters.

        Return the new cursor object."""
        cursor = self.cursor()
        cursor.execute(sql, parameters)
        return cursor

    def executemany(self, sql: str, parameters: Iterable[Any]) -> Cursor:
        """Create a new Cursor object and call executemany() on it with the given sql and parameters.

        Return the new cursor object."""
        cursor = self.cursor()
        cursor.executemany(sql, parameters)
        return cursor

    def executescript(self, sql_script: str) -> Cursor:
        """Create a new Cursor object and call executescript() on it with the given sql_script.

        Return the new cursor object."""
        cursor = self.cursor()
        cursor.executescript(sql_script)
        return cursor

    def create_function(
        self,
        name: str,
        narg: int,
        func: Callable | None,
        *,
        deterministic: bool = False,
    ):
        """Create or remove a user-defined SQL function."""
        raise NotImplementedError()

    def create_aggregate(self, name: str, n_arg: int, aggregate_class: Callable | None):
        """Create or remove a user-defined SQL aggregate function."""
        raise NotImplementedError()

    def create_window_function(
        self, name: str, num_params: Literal[1], aggregate_class: Callable | None
    ):
        """Create or remove a user-defined aggregate window function."""
        raise NotImplementedError()

    def create_collation(self, name: str, callback: Callable | None):
        """Create a collation named name using the collating function callable."""
        raise NotImplementedError()

    def interrupt(self):
        """Call this method from a different thread to abort any queries that might be executing on
        the connection. Aborted queries will raise an OperationalError."""
        raise NotImplementedError()

    def set_authorizer(self, authorizer_callback: Callable | None):
        raise NotImplementedError()

    def set_progress_handler(self, progress_handler: Callable | None, n: int):
        raise NotImplementedError()

    def set_trace_callback(self, trace_callback: Callable | None):
        raise NotImplementedError()

    def enable_load_extension(self, enable: bool):
        raise NotImplementedError()

    def load_extension(self, name: str):
        raise NotImplementedError()

    def iterdump(self) -> Generator:
        raise NotImplementedError()

    def backup(
        self,
        target: Connection,
        *,
        pages: int = -1,
        progress: Callable | None = None,
        name: str = "main",
        sleep: float = 0.25,
    ):
        raise NotImplementedError()

    def setlimit(self, category: int, limit: int) -> int:
        raise NotImplementedError()

    def getlimit(self, category: int) -> int:
        raise NotImplementedError()

    def getconfig(self, op: int) -> bool:
        raise NotImplementedError()

    def setconfig(self, op: int, enable: bool = True) -> bool:
        raise NotImplementedError()

    def serialize(self, *, name: str = "main") -> bytes:
        raise NotImplementedError()

    def deserialize(self, data, *, name: str = "main"):
        raise NotImplementedError()

    def __call__(self, sql: str):
        raise NotImplementedError()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type, value, traceback):
        self.commit()
        return False
