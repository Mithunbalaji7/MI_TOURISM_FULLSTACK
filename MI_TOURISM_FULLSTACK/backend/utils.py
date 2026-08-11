"""
utils.py
--------
Reusable helper functions shared by every backend module:
  - password hashing (hashlib, no external deps)
  - simple session token generation / lookup (stored in MySQL, dummy auth
    is fine for this academic project per project requirements)
  - basic input validation (email, phone, required fields)
  - small JSON response helper
"""

import hashlib
import secrets
import re
import json
from datetime import datetime, timedelta

from db import run_query

SESSION_LIFETIME_HOURS = 12


# ---------------------------------------------------------------------------
# PASSWORD HASHING (SHA-256 + per-user salt). Good enough for a dummy
# academic project; NOT meant for real production use.
# ---------------------------------------------------------------------------
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password, stored_hash):
    try:
        salt, _ = stored_hash.split("$")
    except (ValueError, AttributeError):
        return False
    return hash_password(password, salt) == stored_hash


# ---------------------------------------------------------------------------
# SESSIONS
# ---------------------------------------------------------------------------
def create_session(user_id):
    token = secrets.token_hex(24)
    expires_at = datetime.now() + timedelta(hours=SESSION_LIFETIME_HOURS)
    run_query(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
        (token, user_id, expires_at),
        commit=True,
    )
    return token


def get_user_from_token(token):
    if not token:
        return None
    row = run_query(
        """SELECT u.* FROM sessions s
           JOIN users u ON u.id = s.user_id
           WHERE s.token = %s AND s.expires_at > NOW()""",
        (token,),
        fetch_one=True,
    )
    return row


def delete_session(token):
    run_query("DELETE FROM sessions WHERE token = %s", (token,), commit=True)


def get_token_from_headers(handler):
    """Reads the session token from either the Authorization header
    (Bearer <token>) or a `session_token` cookie."""
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.replace("Bearer ", "").strip()
    cookie_header = handler.headers.get("Cookie", "")
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("session_token="):
            return part.split("=", 1)[1]
    return None


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9]{10}$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email))


def is_valid_phone(phone):
    return bool(phone) and bool(PHONE_RE.match(phone))


def require_fields(data, fields):
    """Returns list of missing/empty field names."""
    missing = []
    for f in fields:
        if data.get(f) in (None, "", []):
            missing.append(f)
    return missing


def json_body_bytes(obj):
    return json.dumps(obj).encode("utf-8")
