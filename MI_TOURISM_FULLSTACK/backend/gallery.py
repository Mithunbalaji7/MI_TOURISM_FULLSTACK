"""
gallery.py
----------
Dynamic photo gallery. Admin "uploads" images (stored as a URL/path since
there is no binary file upload server here); users can filter by category.
"""

from db import run_query
from utils import require_fields


def list_gallery(category=None):
    if category:
        rows = run_query("SELECT * FROM gallery WHERE category = %s ORDER BY uploaded_at DESC", (category,), fetch=True)
    else:
        rows = run_query("SELECT * FROM gallery ORDER BY uploaded_at DESC", fetch=True)
    return 200, {"success": True, "images": rows}


def add_image(data):
    missing = require_fields(data, ["image_url"])
    if missing:
        return 400, {"success": False, "message": "image_url is required."}
    new_id = run_query(
        "INSERT INTO gallery (title, category, image_url) VALUES (%s, %s, %s)",
        (data.get("title", ""), data.get("category", "General"), data["image_url"]),
        commit=True,
    )
    return 201, {"success": True, "message": "Image added to gallery.", "id": new_id}


def delete_image(image_id):
    existing = run_query("SELECT id FROM gallery WHERE id = %s", (image_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Image not found."}
    run_query("DELETE FROM gallery WHERE id = %s", (image_id,), commit=True)
    return 200, {"success": True, "message": "Image deleted."}
