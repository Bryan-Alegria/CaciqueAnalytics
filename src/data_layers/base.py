"""Base layer with database connectivity and shared helpers."""

from typing import Any

from src.db.session import get_connection


class BaseDataLayer:
    """Provides database access and common query utilities."""

    def __init__(self):
        self._conn = None
        self._cur = None

    @property
    def conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = get_connection()
        return self._conn

    @property
    def cur(self):
        if self._cur is None or self._cur.closed:
            self._cur = self.conn.cursor()
        return self._cur

    def execute(self, query: str, params: tuple | None = None) -> None:
        self.cur.execute(query, params or ())

    def fetchone(self) -> tuple | None:
        return self.cur.fetchone()

    def fetchall(self) -> list[tuple]:
        return self.cur.fetchall()

    def close(self) -> None:
        if self._cur and not self._cur.closed:
            self._cur.close()
        if self._conn and not self._conn.closed:
            self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
