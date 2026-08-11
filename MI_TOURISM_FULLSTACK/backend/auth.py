"""
auth.py
-------
Register / Login / Forgot-Password / Logout.
Dummy OTP based password reset (OTP is returned in the API response itself
instead of a real email/SMS, since this is an academic project with no
production email service).
"""

import secrets
from datetime import datetime, timedelta

from db import run_query
from utils import (
    hash_password, verify_password, create_session, delete_session,
    is_valid_email, is_valid_phone, require_fields,
)


def register(data):
    missing = require_fields(data, ["full_name", "email", "password"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    if not is_valid_email(data["email"]):
        return 400, {"success": False, "message": "Invalid email address."}

    if data.get("phone") and not is_valid_phone(data["phone"]):
        return 400, {"success": False, "message": "Phone number must be 10 digits."}

    if len(data["password"]) < 6:
        return 400, {"success": False, "message": "Password must be at least 6 characters."}

    existing = run_query("SELECT id FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if existing:
        return 409, {"success": False, "message": "An account with this email already exists."}

    pwd_hash = hash_password(data["password"])
    user_id = run_query(
        "INSERT INTO users (full_name, email, phone, password_hash) VALUES (%s, %s, %s, %s)",
        (data["full_name"], data["email"], data.get("phone"), pwd_hash),
        commit=True,
    )
    token = create_session(user_id)
    return 201, {"success": True, "message": "Registration successful.", "token": token}


def login(data):
    missing = require_fields(data, ["email", "password"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    user = run_query("SELECT * FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if not user or not verify_password(data["password"], user["password_hash"]):
        return 401, {"success": False, "message": "Invalid email or password."}

    token = create_session(user["id"])
    return 200, {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


def logout(handler_token):
    if handler_token:
        delete_session(handler_token)
    return 200, {"success": True, "message": "Logged out."}


def forgot_password_request(data):
    """Step 1: user submits email -> we generate an OTP (dummy, returned
    directly in the response so it can be shown on-screen for testing,
    since there is no real email/SMS gateway)."""
    missing = require_fields(data, ["email"])
    if missing:
        return 400, {"success": False, "message": "Email is required."}

    user = run_query("SELECT id FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if not user:
        return 404, {"success": False, "message": "No account found with this email."}

    otp = f"{secrets.randbelow(1000000):06d}"
    expires_at = datetime.now() + timedelta(minutes=10)
    run_query(
        "INSERT INTO password_resets (user_id, otp_code, expires_at) VALUES (%s, %s, %s)",
        (user["id"], otp, expires_at),
        commit=True,
    )
    return 200, {
        "success": True,
        "message": "OTP generated (dummy email). Use it to reset your password.",
        "dummy_otp": otp,
    }


def forgot_password_reset(data):
    """Step 2: user submits email + otp + new_password."""
    missing = require_fields(data, ["email", "otp", "new_password"])
    if missing:
        return 400, {"success": False, "message": f"Missing fields: {', '.join(missing)}"}

    user = run_query("SELECT id FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if not user:
        return 404, {"success": False, "message": "No account found with this email."}

    reset_row = run_query(
        """SELECT * FROM password_resets
           WHERE user_id = %s AND otp_code = %s AND used = 0 AND expires_at > NOW()
           ORDER BY id DESC LIMIT 1""",
        (user["id"], data["otp"]),
        fetch_one=True,
    )
    if not reset_row:
        return 400, {"success": False, "message": "Invalid or expired OTP."}

    if len(data["new_password"]) < 6:
        return 400, {"success": False, "message": "Password must be at least 6 characters."}

    new_hash = hash_password(data["new_password"])
    run_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user["id"]), commit=True)
    run_query("UPDATE password_resets SET used = 1 WHERE id = %s", (reset_row["id"],), commit=True)
    return 200, {"success": True, "message": "Password reset successful. Please login."}
