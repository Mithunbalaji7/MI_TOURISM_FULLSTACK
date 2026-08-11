"""
blog.py
-------
Travel blog posts, stored in MySQL. Any logged-in user can write a post;
everyone can read.
"""

from db import run_query
from utils import require_fields


def list_blogs():
    rows = run_query(
        """SELECT b.*, u.full_name AS author_name FROM blogs b
           LEFT JOIN users u ON u.id = b.author_id
           ORDER BY b.created_at DESC""",
        fetch=True,
    )
    return 200, {"success": True, "blogs": rows}


def get_blog(blog_id):
    row = run_query(
        """SELECT b.*, u.full_name AS author_name FROM blogs b
           LEFT JOIN users u ON u.id = b.author_id WHERE b.id = %s""",
        (blog_id,),
        fetch_one=True,
    )
    if not row:
        return 404, {"success": False, "message": "Blog post not found."}
    return 200, {"success": True, "blog": row}


def create_blog(user_id, data):
    missing = require_fields(data, ["title", "content"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}
    new_id = run_query(
        "INSERT INTO blogs (author_id, title, content, image_url) VALUES (%s, %s, %s, %s)",
        (user_id, data["title"], data["content"], data.get("image_url", "")),
        commit=True,
    )
    return 201, {"success": True, "message": "Blog post published.", "id": new_id}


def delete_blog(blog_id):
    existing = run_query("SELECT id FROM blogs WHERE id = %s", (blog_id,), fetch_one=True)
    if not existing:
        return 404, {"success": False, "message": "Blog post not found."}
    run_query("DELETE FROM blogs WHERE id = %s", (blog_id,), commit=True)
    return 200, {"success": True, "message": "Blog post deleted."}
