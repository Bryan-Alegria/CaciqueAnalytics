"""PostgreSQL session management."""

import psycopg2
from psycopg2.extras import RealDictCursor

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_connection():
    """Return a new psycopg2 connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_cursor(conn=None):
    """Return a RealDictCursor. Creates connection if none provided."""
    if conn is None:
        conn = get_connection()
    return conn.cursor(cursor_factory=RealDictCursor)
