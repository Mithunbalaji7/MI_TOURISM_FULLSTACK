"""
feedback.py
-----------
Users submit a star rating + review text for a place. Reviews are displayed
dynamically (fetched via GET) on the feedback page and place detail pages.
"""

from db import run_query
from utils import require_fields


def submit_review(user_id, data):
    missing = require_fields(data, ["place_id", "rating"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    try:
        rating = int(data["rating"])
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        return 400, {"success": False, "message": "Rating must be between 1 and 5."}

    review_id = run_query(
        "INSERT INTO reviews (user_id, place_id, rating, review_text) VALUES (%s, %s, %s, %s)",
        (user_id, data["place_id"], rating, data.get("review_text", "")),
        commit=True,
    )

    # Keep the place's average rating up to date for search/sort/display.
    run_query(
        """UPDATE places SET rating = (
               SELECT ROUND(AVG(rating), 1) FROM reviews WHERE place_id = %s
           ) WHERE id = %s""",
        (data["place_id"], data["place_id"]),
        commit=True,
    )
    return 201, {"success": True, "message": "Thank you for your feedback!", "id": review_id}


def list_reviews(place_id=None):
    if place_id:
        rows = run_query(
            """SELECT r.*, u.full_name FROM reviews r JOIN users u ON u.id = r.user_id
               WHERE r.place_id = %s ORDER BY r.created_at DESC""",
            (place_id,),
            fetch=True,
        )
    else:
        rows = run_query(
            """SELECT r.*, u.full_name, p.name AS place_name FROM reviews r
               JOIN users u ON u.id = r.user_id
               LEFT JOIN places p ON p.id = r.place_id
               ORDER BY r.created_at DESC LIMIT 50""",
            fetch=True,
        )
    return 200, {"success": True, "reviews": rows}
