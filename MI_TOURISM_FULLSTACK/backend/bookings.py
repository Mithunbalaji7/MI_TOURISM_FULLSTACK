"""
bookings.py
-----------
Booking creation + retrieval. Price is calculated server-side from the
package price * members, plus a small surcharge based on vehicle/hotel type,
so the client cannot tamper with the total.
"""

import secrets
from datetime import datetime

from db import run_query
from utils import require_fields

HOTEL_MULTIPLIER = {"Budget": 1.0, "Standard": 1.25, "Luxury": 1.75}
VEHICLE_SURCHARGE = {"None": 0, "Car": 500, "Van": 1200, "Bus": 2500}


def _generate_booking_code():
    return "MITD" + secrets.token_hex(4).upper()


def calculate_total(package_price, members, vehicle_type, hotel_type):
    base = float(package_price) * int(members)
    base *= HOTEL_MULTIPLIER.get(hotel_type, 1.0)
    base += VEHICLE_SURCHARGE.get(vehicle_type, 0)
    return round(base, 2)


def create_booking(user_id, data):
    missing = require_fields(data, ["package_id", "travel_date", "members"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    package = run_query("SELECT * FROM packages WHERE id = %s", (data["package_id"],), fetch_one=True)
    if not package:
        return 404, {"success": False, "message": "Selected package does not exist."}

    try:
        travel_date = datetime.strptime(data["travel_date"], "%Y-%m-%d").date()
    except ValueError:
        return 400, {"success": False, "message": "travel_date must be in YYYY-MM-DD format."}

    if travel_date < datetime.now().date():
        return 400, {"success": False, "message": "Travel date cannot be in the past."}

    try:
        members = int(data["members"])
        if members < 1:
            raise ValueError
    except ValueError:
        return 400, {"success": False, "message": "Members must be a positive number."}

    vehicle_type = data.get("vehicle_type", "None")
    hotel_type = data.get("hotel_type", "Standard")
    total = calculate_total(package["price"], members, vehicle_type, hotel_type)
    booking_code = _generate_booking_code()

    booking_id = run_query(
        """INSERT INTO bookings
           (user_id, package_id, travel_date, members, vehicle_type, hotel_type, total_amount, booking_code)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (user_id, data["package_id"], travel_date, members, vehicle_type, hotel_type, total, booking_code),
        commit=True,
    )
    return 201, {
        "success": True,
        "message": "Booking created. Proceed to payment.",
        "booking_id": booking_id,
        "booking_code": booking_code,
        "total_amount": total,
    }


def list_user_bookings(user_id):
    rows = run_query(
        """SELECT b.*, p.title AS package_title, p.image_url FROM bookings b
           JOIN packages p ON p.id = b.package_id
           WHERE b.user_id = %s ORDER BY b.created_at DESC""",
        (user_id,),
        fetch=True,
    )
    return 200, {"success": True, "bookings": rows}


def list_all_bookings():
    rows = run_query(
        """SELECT b.*, p.title AS package_title, u.full_name, u.email FROM bookings b
           JOIN packages p ON p.id = b.package_id
           JOIN users u ON u.id = b.user_id
           ORDER BY b.created_at DESC""",
        fetch=True,
    )
    return 200, {"success": True, "bookings": rows}


def get_booking(booking_id, user_id=None):
    query = """SELECT b.*, p.title AS package_title, u.full_name, u.email FROM bookings b
               JOIN packages p ON p.id = b.package_id
               JOIN users u ON u.id = b.user_id
               WHERE b.id = %s"""
    params = [booking_id]
    if user_id is not None:
        query += " AND b.user_id = %s"
        params.append(user_id)
    row = run_query(query, tuple(params), fetch_one=True)
    if not row:
        return 404, {"success": False, "message": "Booking not found."}
    return 200, {"success": True, "booking": row}
