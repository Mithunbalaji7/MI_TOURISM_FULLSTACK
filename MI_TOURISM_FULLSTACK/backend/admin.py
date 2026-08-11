"""
admin.py
--------
Admin-only operations: view users, search users, view all bookings.
Place / package CRUD lives in places.py / packages.py and is reused here by
the router (kept there so those modules stay the single source of truth for
that data, avoiding duplicate code).
"""

from db import run_query


def list_users():
    rows = run_query(
        "SELECT id, full_name, email, phone, role, created_at FROM users ORDER BY created_at DESC",
        fetch=True,
    )
    return 200, {"success": True, "users": rows}


def search_users(keyword):
    keyword = f"%{keyword}%"
    rows = run_query(
        """SELECT id, full_name, email, phone, role, created_at FROM users
           WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s
           ORDER BY created_at DESC""",
        (keyword, keyword, keyword),
        fetch=True,
    )
    return 200, {"success": True, "users": rows}
