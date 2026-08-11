"""
db.py
-----
Centralised MySQL connection handling for the MI Tourism Development backend.

Every other backend module imports `get_connection()` from here instead of
opening its own connection. This keeps DB credentials in ONE place and makes
the code reusable / DRY (no duplicate connection code across modules).

Requires: mysql-connector-python
    pip install mysql-connector-python
"""

import mysql.connector
from mysql.connector import pooling

# ---------------------------------------------------------------------------
# DATABASE CONFIGURATION
# Change these values to match your local MySQL setup.
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root123",          # <-- change to your MySQL root/user password
    "database": "mi_tourism_db",
}

# A small connection pool avoids opening/closing a fresh TCP connection for
# every single request, which matters once booking/search/admin endpoints
# are all hitting MySQL.
_pool = None


def _init_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="mi_tourism_pool",
            pool_size=5,
            **DB_CONFIG,
        )
    return _pool


def get_connection():
    """Return a live connection from the pool.

    Falls back to a direct (non-pooled) connection if the pool cannot be
    created (e.g. MySQL not reachable yet during first-time setup), so the
    caller always gets a clear mysql.connector error instead of a confusing
    pool error.
    """
    try:
        pool = _init_pool()
        return pool.get_connection()
    except mysql.connector.Error:
        return mysql.connector.connect(**DB_CONFIG)


def run_query(query, params=None, fetch=False, fetch_one=False, commit=False):
    """Generic helper used by every module for simple CRUD calls.

    - fetch=True      -> returns list of dict rows
    - fetch_one=True  -> returns a single dict row (or None)
    - commit=True     -> commits and returns the new row's lastrowid
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            result = cursor.lastrowid
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()
