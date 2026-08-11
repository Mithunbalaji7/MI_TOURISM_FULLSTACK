"""
search.py
---------
Search tourist places by keyword with District / Category / Budget / Rating
filters. Also logs the search term against the logged-in user's recent
searches (used on the dashboard) when a user_id is supplied.
"""

from db import run_query


def search_places(params, user_id=None):
    keyword = params.get("q", "").strip()
    query = "SELECT p.*, MIN(pk.price) AS from_price FROM places p LEFT JOIN packages pk ON pk.place_id = p.id WHERE 1=1"
    args = []

    if keyword:
        query += " AND (p.name LIKE %s OR p.description LIKE %s)"
        args += [f"%{keyword}%", f"%{keyword}%"]

    if params.get("district"):
        query += " AND p.district = %s"
        args.append(params["district"])

    if params.get("category"):
        query += " AND p.category = %s"
        args.append(params["category"])

    if params.get("min_rating"):
        query += " AND p.rating >= %s"
        args.append(float(params["min_rating"]))

    query += " GROUP BY p.id"

    if params.get("max_budget"):
        query += " HAVING (from_price IS NULL OR from_price <= %s)"
        args.append(float(params["max_budget"]))

    query += " ORDER BY p.rating DESC"

    rows = run_query(query, tuple(args), fetch=True)

    if user_id and keyword:
        run_query(
            "INSERT INTO recent_searches (user_id, search_term) VALUES (%s, %s)",
            (user_id, keyword),
            commit=True,
        )

    return 200, {"success": True, "results": rows, "count": len(rows)}
