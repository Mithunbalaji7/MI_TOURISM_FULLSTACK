"""
news.py
-------
Dynamic "Latest Tourism News" section, stored in MySQL and managed by admin.
"""

from db import run_query
from utils import require_fields


def list_news():
    rows = run_query("SELECT * FROM news ORDER BY published_at DESC", fetch=True)
    return 200, {"success": True, "news": rows}


def create_news(data):
    missing = require_fields(data, ["title", "content"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}
    new_id = run_query(
        "INSERT INTO news (title, content, image_url) VALUES (%s, %s, %s)",
        (data["title"], data["content"], data.get("image_url", "")),
        commit=True,
    )
    return 201, {"success": True, "message": "News published.", "id": new_id}


def delete_news(news_id):
    existing = run_query("SELECT id FROM news WHERE id = %s", (news_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "News item not found."}
    run_query("DELETE FROM news WHERE id = %s", (news_id,), commit=True)
    return 200, {"success": True, "message": "News item deleted."}
