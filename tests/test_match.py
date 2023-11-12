import sqlite3
import sqlite3_qt

from pytest import mark
from sqlite3_qt.qt_compat import QT_API


def compare_modules(func):
    """Compare outputs of func using sqlite3 vs. sqlite3-qt"""

    def compare(*args, **kwargs):
        assert func(*args, **kwargs, module=sqlite3) == func(
            *args, **kwargs, module=sqlite3_qt
        )

    return compare


def test_1():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE movie(title, year, score)")
        cur = cur.execute("SELECT name FROM sqlite_master")
        res = cur.fetchone()
        con.close()
        return res

    return op()


def test_2():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE movie(title, year, score)")
        cur = cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
        res = cur.fetchone() is None
        con.close()
        return res

    return op()


def test_3():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE movie(title, year, score)")
        cur.execute(
            """INSERT INTO movie VALUES
        ('Monty Python and the Holy Grail', 1975, 8.2),
        ('And Now for Something Completely Different', 1971, 7.5)
"""
        )
        con.commit()
        cur = cur.execute("SELECT score FROM movie")
        res = cur.fetchall()
        con.close()
        return res

    return op()


def test_4():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE movie(title, year, score)")
        data = [
            ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
            ("Monty Python's The Meaning of Life", 1983, 7.5),
            ("Monty Python's Life of Brian", 1979, 8.0),
        ]
        cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
        con.commit()
        res = [
            row for row in cur.execute("SELECT year, title FROM movie ORDER BY year")
        ]
        con.close()
        return res

    return op()


def test_5():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE movie(title, year, score)")
        data = ("Monty Python Live at the Hollywood Bowl", 1982, 7.9)
        cur.execute("INSERT INTO movie VALUES(?, ?, ?)", data)
        con.commit()
        res = [
            row for row in cur.execute("SELECT year, title FROM movie ORDER BY year")
        ]
        con.close()
        return res

    return op()

@mark.skipif(QT_API=='PySide2', reason='PySide2 does not support value binding.')
def test_6():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE test(bytes BLOB)")
        data = ("a;lksdfj;asdf".encode("utf8"),)
        cur.execute("INSERT INTO test VALUES(?)", data)
        con.commit()
        res = [row for row in cur.execute("SELECT bytes FROM test")]
        con.close()
        return res

    return op()


@mark.skipif(QT_API=='PySide2', reason='PySide2 does not support value binding.')
def test_7():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE test(bytes BLOB)")
        data = [
            ("a;lksdfj;asdf".encode("utf8"),),
            ("a;slkfj;alsjfasdf".encode("utf8"),),
        ]
        cur.executemany("INSERT INTO test VALUES(?)", data)
        con.commit()
        res = [row for row in cur.execute("SELECT bytes FROM test")]
        con.close()
        return res

    return op()


@mark.skipif(QT_API=='PySide2', reason='PySide2 does not support value binding.')
def test_8():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE test(bytes BLOB)")
        data = {"x": "a;lksdfj;asdf".encode("utf8")}
        cur.execute("INSERT INTO test VALUES(:x)", data)
        con.commit()
        res = [row for row in cur.execute("SELECT bytes FROM test")]
        con.close()
        return res

    return op()

@mark.skipif(QT_API=='PySide2', reason='PySide2 does not support value binding.')
def test_9():
    @compare_modules
    def op(module=None):
        con = module.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE test(bytes BLOB)")
        data = [
            {"x": "a;lksdfj;asdf".encode("utf8")},
            {"x": "a;slkfj;alsjfasdf".encode("utf8")},
        ]
        cur.executemany("INSERT INTO test VALUES(:x)", data)
        con.commit()
        res = [row for row in cur.execute("SELECT bytes FROM test")]
        con.close()
        return res

    return op()
