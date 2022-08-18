# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import sqlite3
import pathlib
import contextlib

# Custom Library
from AthenaLib.data.text import NOTHING

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class Translation:
    sqlite_filepath:str=NOTHING
    conn: sqlite3.Connection|None = None

    def __init__(self, sqlite_filepath:str=NOTHING):
            self.sqlite_filepath = sqlite_filepath

    # ------------------------------------------------------------------------------------------------------------------
    # - Connection and Cursor context managers -
    # ------------------------------------------------------------------------------------------------------------------
    @contextlib.contextmanager
    def gather_connection(self) -> sqlite3.Connection:
        """
        Context Managed function to yield the connection to any function that needs it.
        Closes the connection automatically
        """
        # Check if the sqlite file is actually present
        if not pathlib.Path(self.sqlite_filepath).exists():
            raise ValueError(f"'{self.sqlite_filepath}' does not exist")

        # Context manage the connection
        #   Done so the connection always auto closes
        with contextlib.closing(sqlite3.connect(self.sqlite_filepath)) as conn: #type:  sqlite3.Connection
            yield conn

    @contextlib.contextmanager
    def gather_cursor(self) -> sqlite3.Cursor:
        """
        Context Managed function to yield the cursor to any function that needs it.
        Calls the Translation.gather_connection() first to have the connection managed through there.
        Closes the cursor automatically
        """

        # Context manage the cursor
        #   Done so the connection always auto closes
        with self.gather_connection() as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                yield cursor