# sqlite_helper.py
#
# Copyright (C) 2021 Katie Stafford (katie@ktpanda.org)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
sqlite_helper
=============

A wrapper class for an SQLite database that includes schema versioning and
various helper methods.
'''

import sys
import sqlite3
import functools

def retry(func, *args):
    while True:
        try:
            return func(*args)
        except sqlite3.OperationalError as err:
            if str(err) != 'database is locked':
                raise

def in_transaction(f):
    '''Decorator for methods which write to the database which wraps the function in a call to retry_transaction.'''
    def wrapper(self, *a, **kw):
        return self.retry_transaction(f, self, *a, **kw)
    functools.update_wrapper(wrapper, f)
    return wrapper

def split_schema(text):
    '''Split `text` into a list of individual SQL statements. Each statement should be
    terminated by a double-semicolon (;;). This allows for the definition of triggers
    which contain multiple statements.'''
    lst = [statement.strip() for statement in text.split(';;')]
    return [statement for statement in lst if statement]

class SQLiteDB(object):
    journal_mode = 'WAL'
    synchronous_mode = 'NORMAL'
    page_size = 8192
    recursive_triggers = True
    legacy_file_format = False
    foreign_keys = True

    common_schema = ['''
    CREATE TABLE IF NOT EXISTS vars (
      name TEXT PRIMARY KEY,
      value
    ) WITHOUT ROWID
    ''']

    schema_version = 1

    def __init__(self, backend):
        self.backend = backend
        self.explain = False
        self.explained = set()

        self.exec_schema(self._get_common_commands())
        self._check_version()

    def exec_schema(self, schema):
        for cmd in schema:
            if not cmd.strip():
                continue

            try:
                self.backend.execute(cmd)
            except Exception:
                print(f'Error executing {cmd}', file=sys.stderr)
                raise

    def _check_version(self):
        cvers = self.backend.execute('PRAGMA user_version').fetchone()[0]
        if cvers < self.schema_version:
            self.backend.execute('BEGIN EXCLUSIVE')
            if cvers != 0:
                self._do_upgrade(cvers, self.schema_version, 'upgrade')

            self.exec_schema(self.common_schema)
            if cvers == 0:
                self._init_db()
            else:
                self._do_upgrade(cvers, self.schema_version, 'postupgrade')
            self.backend.execute(f'PRAGMA user_version = {self.schema_version}')
            self.commit()

    def _init_db(self):
        pass

    def _do_upgrade(self, oldvers, newvers, func):
        for v in range(oldvers + 1, newvers + 1):
            ugf = getattr(self, f'_{func}_to_{v}', None)
            if ugf:
                ugf(oldvers)

    def _get_common_commands(self):
        return [
            f'PRAGMA journal_mode = {self.journal_mode}',
            f'PRAGMA synchronous = {self.synchronous_mode}',
            f'PRAGMA page_size = {self.page_size}',
            f'PRAGMA recursive_triggers = {"ON" if self.recursive_triggers else "OFF"}',
            f'PRAGMA legacy_file_format = {"ON" if self.legacy_file_format else "OFF"}',
            f'PRAGMA foreign_keys = {"ON" if self.foreign_keys else "OFF"}'
        ]

    def alter_schema(self, *mods, check=True):
        sqlite_schema_version = list(self.backend.execute('PRAGMA schema_version'))[0][0]

        self.backend.execute('PRAGMA writable_schema = ON')

        for select_criteria, args, prefix, old, new, suffix in mods:
            #type = 'table' AND name = 'test_case_run_ticket'
            self.backend.execute(f"UPDATE sqlite_master SET sql = REPLACE(sql, ?, ?) WHERE {select_criteria}",
                                 (prefix + old + suffix, prefix + new + suffix) + args)

        self.backend.execute(f'PRAGMA schema_version = {sqlite_schema_version + 1}')
        self.backend.execute('PRAGMA writable_schema = OFF')
        if check:
            self.backend.execute('PRAGMA integrity_check')

    def commit(self):
        return self.backend.commit()

    def rollback(self):
        self.backend.execute('ROLLBACK')

    def _do_explain(self, q, args):
        if q in self.explained:
            return
        self.explained.add(q)
        print()
        print('=== ' + q)
        for row in self.backend.execute('EXPLAIN QUERY PLAN ' + q, args):
            print(f'   {row!r}')
        print()

    def select_one(self, q, args=(), default=None):
        curs = self.execute(q, args)
        try:
            return next(curs)
        except StopIteration:
            return default

    def select_scalar(self, q, args=(), default=None):
        return self.select_one(q, args, (default,))[0]

    def execute(self, q, args=(), mod=True):
        if self.explain:
            self._do_explain(q, args)

        while True:
            try:
                curs = self.backend.cursor()
                curs.execute(q, args)
                return curs
            except sqlite3.OperationalError as err:
                if self._in_transaction or str(err) != 'database is locked':
                    raise

    def executemany(self, *args):
        curs = self.backend.cursor()
        curs.executemany(*args)
        return curs

    def close(self):
        self.backend.close()

    def getvar(self, name, default=None):
        row = self.select('value FROM vars WHERE name = ?', (name,)).fetchone()
        if row:
            return row[0]
        return default

    def setvar(self, name, val):
        self.execute('INSERT OR REPLACE INTO vars VALUES(?, ?)', (name, val))

    def retry_transaction(self, func, *a, **kw):
        '''Begin a transaction and run func(). If the database is locked, rolls back and
        runs func() again until it succeeds. If it fails with any other exception, the
        database is rolled back
        '''
        committed = False
        begin = 'BEGIN'
        while True:
            try:
                self.backend.execute(begin)
                rv = func(*a, **kw)
                self.commit()
                committed = True
                return rv
            except sqlite3.OperationalError as err:
                if str(err) != 'database is locked':
                    raise

                # If func() tried to change the database but a conflict occured, then next
                # time we run, grab the write lock immediately.
                begin = 'BEGIN IMMEDIATE'
            finally:
                if not committed:
                    self.rollback()
