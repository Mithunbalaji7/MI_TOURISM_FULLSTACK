"""
places.py
---------
Tourist places CRUD + homepage dynamic sections (featured / trending /
popular) + tourist statistics for the animated counters.
"""

from db import run_query
from utils import require_fields


def list_places(filters=None):
    filters = filters or {}
    query = "SELECT * FROM places WHERE 1=1"
    params = []

    if filters.get("district"):
        query += " AND district = %s"
        params.append(filters["district"])
    if filters.get("category"):
        query += " AND category = %s"
        params.append(filters["category"])
    if filters.get("min_rating"):
        query += " AND rating >= %s"
        params.append(float(filters["min_rating"]))

    query += " ORDER BY rating DESC"
    rows = run_query(query, tuple(params), fetch=True)
    return 200, {"success": True, "places": rows}


def get_place(place_id):
    row = run_query("SELECT * FROM places WHERE id = %s", (place_id,), fetch_one=True)
    if not row:
        return 404, {"success": False, "message": "Place not found."}
    return 200, {"success": True, "place": row}


def featured_places():
    rows = run_query("SELECT * FROM places WHERE is_featured = 1 ORDER BY rating DESC LIMIT 6", fetch=True)
    return 200, {"success": True, "places": rows}


def trending_packages():
    rows = run_query(
        """SELECT p.*, pl.name AS place_name FROM packages p
           LEFT JOIN places pl ON pl.id = p.place_id
           WHERE p.is_trending = 1 ORDER BY p.created_at DESC LIMIT 6""",
        fetch=True,
    )
    return 200, {"success": True, "packages": rows}


def popular_attractions():
    rows = run_query("SELECT * FROM places ORDER BY rating DESC LIMIT 8", fetch=True)
    return 200, {"success": True, "places": rows}


def tourist_statistics():
    rows = run_query("SELECT stat_key, stat_value FROM site_stats", fetch=True)
    stats = {r["stat_key"]: r["stat_value"] for r in rows}
    return 200, {"success": True, "stats": stats}


# --- Admin CRUD -------------------------------------------------------------
def create_place(data):
    missing = require_fields(data, ["name", "district"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}
    new_id = run_query(
        """INSERT INTO places (name, district, category, description, image_url, rating, is_trending, is_featured)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data["name"], data["district"], data.get("category", "Regular"),
            data.get("description", ""), data.get("image_url", ""),
            data.get("rating", 0), int(bool(data.get("is_trending"))), int(bool(data.get("is_featured"))),
        ),
        commit=True,
    )
    return 201, {"success": True, "message": "Place added.", "id": new_id}


def update_place(place_id, data):
    existing = run_query("SELECT id FROM places WHERE id = %s", (place_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Place not found."}

    fields, params = [], []
    for col in ["name", "district", "category", "description", "image_url", "rating", "is_trending", "is_featured"]:
        if col in data:
            fields.append(f"{col} = %s")
            params.append(data[col])
    if not fields:
        return 400, {"success": False, "message": "No fields to update."}

    params.append(place_id)
    run_query(f"UPDATE places SET {', '.join(fields)} WHERE id = %s", tuple(params), commit=True)
    return 200, {"success": True, "message": "Place updated."}


def delete_place(place_id):
    existing = run_query("SELECT id FROM places WHERE id = %s", (place_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Place not found."}
    run_query("DELETE FROM places WHERE id = %s", (place_id,), commit=True)
    return 200, {"success": True, "message": "Place deleted."}
