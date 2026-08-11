"""
notifications.py
----------------
Dummy in-app notification system (booking confirmations, admin announcements).
"""

from db import run_query


def list_notifications(user_id):
    rows = run_query(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
        (user_id,), fetch=True,
    )
    return 200, {"success": True, "notifications": rows}


def mark_read(user_id, notification_id):
    run_query(
        "UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s",
        (notification_id, user_id), commit=True,
    )
    return 200, {"success": True, "message": "Notification marked as read."}
