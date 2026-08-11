"""
payment.py
----------
Dummy payment gateway. No real payment provider is contacted - a
transaction reference is generated and the booking is marked Confirmed.
Supports UPI / Card / Net Banking (selected on the frontend payment page).
"""

import secrets

from db import run_query
from utils import require_fields

VALID_METHODS = {"UPI", "Card", "Net Banking"}


def pay(user_id, data):
    missing = require_fields(data, ["booking_id", "method"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    if data["method"] not in VALID_METHODS:
        return 400, {"success": False, "message": "Invalid payment method."}

    booking = run_query(
        "SELECT * FROM bookings WHERE id = %s AND user_id = %s",
        (data["booking_id"], user_id),
        fetch_one=True,
    )
    if not booking:
        return 404, {"success": False, "message": "Booking not found."}

    if booking["status"] == "Confirmed":
        return 409, {"success": False, "message": "This booking is already paid for."}

    # --- Dummy method-specific "validation" (format only, nothing is charged) ---
    if data["method"] == "UPI":
        upi_id = data.get("upi_id", "")
        if "@" not in upi_id:
            return 400, {"success": False, "message": "Enter a valid UPI ID (e.g. name@bank)."}
    elif data["method"] == "Card":
        card_number = data.get("card_number", "").replace(" ", "")
        if not (card_number.isdigit() and len(card_number) in (15, 16)):
            return 400, {"success": False, "message": "Enter a valid card number."}
    elif data["method"] == "Net Banking":
        if not data.get("bank_name"):
            return 400, {"success": False, "message": "Select a bank."}

    txn_ref = "TXN" + secrets.token_hex(8).upper()

    run_query(
        """INSERT INTO payments (booking_id, method, amount, status, transaction_ref)
           VALUES (%s, %s, %s, 'Success', %s)""",
        (booking["id"], data["method"], booking["total_amount"], txn_ref),
        commit=True,
    )
    run_query("UPDATE bookings SET status = 'Confirmed' WHERE id = %s", (booking["id"],), commit=True)

    # Dummy notification + dummy email confirmation
    run_query(
        "INSERT INTO notifications (user_id, title, message) VALUES (%s, %s, %s)",
        (user_id, "Booking Confirmed", f"Your booking {booking['booking_code']} is confirmed."),
        commit=True,
    )

    return 200, {
        "success": True,
        "message": "Payment successful. Booking confirmed.",
        "transaction_ref": txn_ref,
        "booking_code": booking["booking_code"],
        "amount": float(booking["total_amount"]),
        "email_sent_to": _get_user_email(user_id),
    }


def _get_user_email(user_id):
    row = run_query("SELECT email FROM users WHERE id = %s", (user_id,), fetch_one=True)
    return row["email"] if row else None
