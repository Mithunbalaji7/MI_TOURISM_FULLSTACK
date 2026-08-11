"""
contact.py
----------
Stores Contact Us form submissions (name, email, phone, message) in MySQL.
"""

from db import run_query
from utils import require_fields, is_valid_email, is_valid_phone


def submit_contact(data):
    missing = require_fields(data, ["name", "email", "message"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    if not is_valid_email(data["email"]):
        return 400, {"success": False, "message": "Invalid email address."}

    if data.get("phone") and not is_valid_phone(data["phone"]):
        return 400, {"success": False, "message": "Phone number must be 10 digits."}

    run_query(
        "INSERT INTO contact_messages (name, email, phone, message) VALUES (%s, %s, %s, %s)",
        (data["name"], data["email"], data.get("phone"), data["message"]),
        commit=True,
    )
    return 201, {"success": True, "message": "Thank you! Your message has been received."}


def list_contact_messages():
    rows = run_query("SELECT * FROM contact_messages ORDER BY created_at DESC", fetch=True)
    return 200, {"success": True, "messages": rows}
