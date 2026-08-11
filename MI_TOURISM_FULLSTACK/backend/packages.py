"""
packages.py
-----------
Tour package CRUD (used by admin panel + booking module + homepage).
"""

from db import run_query
from utils import require_fields


def list_packages():
    rows = run_query(
        """SELECT p.*, pl.name AS place_name FROM packages p
           LEFT JOIN places pl ON pl.id = p.place_id
           ORDER BY p.created_at DESC""",
        fetch=True,
    )
    return 200, {"success": True, "packages": rows}


def get_package(package_id):
    row = run_query(
        """SELECT p.*, pl.name AS place_name FROM packages p
           LEFT JOIN places pl ON pl.id = p.place_id
           WHERE p.id = %s""",
        (package_id,),
        fetch_one=True,
    )
    if not row:
        return 404, {"success": False, "message": "Package not found."}
    return 200, {"success": True, "package": row}


def create_package(data):
    missing = require_fields(data, ["title", "price"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}
    new_id = run_query(
        """INSERT INTO packages (place_id, title, description, duration_days, price, image_url, is_trending)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            data.get("place_id"), data["title"], data.get("description", ""),
            data.get("duration_days", 1), data["price"], data.get("image_url", ""),
            int(bool(data.get("is_trending"))),
        ),
        commit=True,
    )
    return 201, {"success": True, "message": "Package added.", "id": new_id}


def update_package(package_id, data):
    existing = run_query("SELECT id FROM packages WHERE id = %s", (package_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Package not found."}

    fields, params = [], []
    for col in ["place_id", "title", "description", "duration_days", "price", "image_url", "is_trending"]:
        if col in data:
            fields.append(f"{col} = %s")
            params.append(data[col])
    if not fields:
        return 400, {"success": False, "message": "No fields to update."}

    params.append(package_id)
    run_query(f"UPDATE packages SET {', '.join(fields)} WHERE id = %s", tuple(params), commit=True)
    return 200, {"success": True, "message": "Package updated."}


def delete_package(package_id):
    existing = run_query("SELECT id FROM packages WHERE id = %s", (package_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Package not found."}
    run_query("DELETE FROM packages WHERE id = %s", (package_id,), commit=True)
    return 200, {"success": True, "message": "Package deleted."}
