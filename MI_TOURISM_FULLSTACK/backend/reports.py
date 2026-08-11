"""
reports.py
----------
Admin dashboard reports: bookings, users, revenue (dummy - based only on
recorded `payments` rows, no real accounting).
"""

from db import run_query


def booking_report():
    summary = run_query(
        """SELECT status, COUNT(*) AS count FROM bookings GROUP BY status""",
        fetch=True,
    )
    total = run_query("SELECT COUNT(*) AS total FROM bookings", fetch_one=True)
    return 200, {"success": True, "by_status": summary, "total_bookings": total["total"]}


def user_report():
    total_users = run_query("SELECT COUNT(*) AS total FROM users WHERE role = 'user'", fetch_one=True)
    new_this_month = run_query(
        """SELECT COUNT(*) AS total FROM users
           WHERE role = 'user' AND MONTH(created_at) = MONTH(CURDATE())
           AND YEAR(created_at) = YEAR(CURDATE())""",
        fetch_one=True,
    )
    top_bookers = run_query(
        """SELECT u.full_name, u.email, COUNT(b.id) AS booking_count FROM users u
           JOIN bookings b ON b.user_id = u.id
           GROUP BY u.id ORDER BY booking_count DESC LIMIT 5""",
        fetch=True,
    )
    return 200, {
        "success": True,
        "total_users": total_users["total"],
        "new_this_month": new_this_month["total"],
        "top_bookers": top_bookers,
    }


def revenue_report():
    total = run_query("SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE status = 'Success'", fetch_one=True)
    by_method = run_query(
        """SELECT method, COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
           FROM payments WHERE status = 'Success' GROUP BY method""",
        fetch=True,
    )
    monthly = run_query(
        """SELECT DATE_FORMAT(paid_at, '%Y-%m') AS month, COALESCE(SUM(amount), 0) AS total
           FROM payments WHERE status = 'Success'
           GROUP BY month ORDER BY month DESC LIMIT 12""",
        fetch=True,
    )
    return 200, {
        "success": True,
        "total_revenue": float(total["total"]),
        "by_method": by_method,
        "monthly": monthly,
    }
