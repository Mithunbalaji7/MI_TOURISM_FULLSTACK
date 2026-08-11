"""
profile.py
----------
Edit profile, change password, update profile picture, dashboard summary
(booking history, favourites, recent searches), and dummy notifications.
"""

from db import run_query
from utils import hash_password, verify_password, require_fields, is_valid_phone


def get_dashboard(user_id):
    user = run_query(
        "SELECT id, full_name, email, phone, role, profile_picture, created_at FROM users WHERE id = %s",
        (user_id,), fetch_one=True,
    )
    if not user:
        return 404, {"success": False, "message": "User not found."}

    bookings = run_query(
        """SELECT b.*, p.title AS package_title FROM bookings b
           JOIN packages p ON p.id = b.package_id
           WHERE b.user_id = %s ORDER BY b.created_at DESC LIMIT 10""",
        (user_id,), fetch=True,
    )
    favourites = run_query(
        """SELECT f.id AS favourite_id, pl.* FROM favourites f
           JOIN places pl ON pl.id = f.place_id
           WHERE f.user_id = %s ORDER BY f.created_at DESC""",
        (user_id,), fetch=True,
    )
    recent_searches = run_query(
        "SELECT search_term, searched_at FROM recent_searches WHERE user_id = %s ORDER BY searched_at DESC LIMIT 10",
        (user_id,), fetch=True,
    )

    return 200, {
        "success": True,
        "user": user,
        "booking_history": bookings,
        "favourite_places": favourites,
        "recent_searches": recent_searches,
    }


def update_profile(user_id, data):
    fields, params = [], []
    if "full_name" in data and data["full_name"]:
        fields.append("full_name = %s")
        params.append(data["full_name"])
    if "phone" in data and data["phone"]:
        if not is_valid_phone(data["phone"]):
            return 400, {"success": False, "message": "Phone number must be 10 digits."}
        fields.append("phone = %s")
        params.append(data["phone"])
    if "profile_picture" in data and data["profile_picture"]:
        fields.append("profile_picture = %s")
        params.append(data["profile_picture"])

    if not fields:
        return 400, {"success": False, "message": "No fields to update."}

    params.append(user_id)
    run_query(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", tuple(params), commit=True)
    return 200, {"success": True, "message": "Profile updated."}


def change_password(user_id, data):
    missing = require_fields(data, ["current_password", "new_password"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    user = run_query("SELECT password_hash FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if not user or not verify_password(data["current_password"], user["password_hash"]):
        return 401, {"success": False, "message": "Current password is incorrect."}

    if len(data["new_password"]) < 6:
        return 400, {"success": False, "message": "New password must be at least 6 characters."}

    new_hash = hash_password(data["new_password"])
    run_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id), commit=True)
    return 200, {"success": True, "message": "Password changed successfully."}


def toggle_favourite(user_id, data):
    missing = require_fields(data, ["place_id"])
    if missing:
        return 400, {"success": False, "message": "place_id is required."}

    existing = run_query(
        "SELECT id FROM favourites WHERE user_id = %s AND place_id = %s",
        (user_id, data["place_id"]), fetch_one=True,
    )
    if existing:
        run_query("DELETE FROM favourites WHERE id = %s", (existing["id"],), commit=True)
        return 200, {"success": True, "message": "Removed from favourites.", "favourited": False}

    run_query(
        "INSERT INTO favourites (user_id, place_id) VALUES (%s, %s)",
        (user_id, data["place_id"]), commit=True,
    )
    return 201, {"success": True, "message": "Added to favourites.", "favourited": True}
