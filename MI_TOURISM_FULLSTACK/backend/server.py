"""
server.py
---------
Main entry point for the MI Tourism Development backend.

Pure Python only - built on the standard library's http.server module
(no Flask / Django, as required). Provides:
  1. A small JSON REST API under /api/...
  2. Static file serving for the existing frontend (HTML/CSS/JS/images) so
     the whole site can be opened from a single "python server.py" command.

Run:
    cd backend
    python server.py
Then open:
    http://localhost:8000/HOME.html
"""

import json
import os
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import auth
import places
import packages
import bookings
import payment
import admin
import search
import contact
import feedback
import news
import gallery
import blog
import profile as profile_module
import notifications
import reports
from utils import get_user_from_token, get_token_from_headers, json_body_bytes

PORT = 8000
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


class Router:
    """Maps (method, path pattern) -> handler function.
    Path params like /api/places/{id} are supported via {name} placeholders.
    """

    def __init__(self):
        self.routes = []  # list of (method, [segments], handler, needs_auth, admin_only)

    def add(self, method, path, handler, auth_required=False, admin_only=False):
        segments = [seg for seg in path.strip("/").split("/")]
        self.routes.append((method.upper(), segments, handler, auth_required, admin_only))

    def match(self, method, path):
        req_segments = [seg for seg in path.strip("/").split("/") if seg != ""]
        for r_method, segments, handler, auth_required, admin_only in self.routes:
            if r_method != method:
                continue
            if len(segments) != len(req_segments):
                continue
            params = {}
            ok = True
            for pattern_seg, real_seg in zip(segments, req_segments):
                if pattern_seg.startswith("{") and pattern_seg.endswith("}"):
                    params[pattern_seg[1:-1]] = real_seg
                elif pattern_seg != real_seg:
                    ok = False
                    break
            if ok:
                return handler, params, auth_required, admin_only
        return None, None, False, False


router = Router()

# ---------------------------------------------------------------------------
# ROUTE DEFINITIONS
# Each handler: fn(data, params, user) -> (status_code, response_dict)
# ---------------------------------------------------------------------------

# ---- AUTH ----
router.add("POST", "/api/auth/register", lambda data, params, user: auth.register(data))
router.add("POST", "/api/auth/login", lambda data, params, user: auth.login(data))
router.add("POST", "/api/auth/forgot-password", lambda data, params, user: auth.forgot_password_request(data))
router.add("POST", "/api/auth/reset-password", lambda data, params, user: auth.forgot_password_reset(data))
router.add("POST", "/api/auth/logout", lambda data, params, user: (200, {"success": True}), auth_required=True)

# ---- HOMEPAGE DYNAMIC DATA ----
router.add("GET", "/api/home/featured", lambda data, params, user: places.featured_places())
router.add("GET", "/api/home/trending-packages", lambda data, params, user: places.trending_packages())
router.add("GET", "/api/home/popular", lambda data, params, user: places.popular_attractions())
router.add("GET", "/api/home/stats", lambda data, params, user: places.tourist_statistics())

# ---- PLACES ----
router.add("GET", "/api/places", lambda data, params, user: places.list_places(data))
router.add("GET", "/api/places/{id}", lambda data, params, user: places.get_place(params["id"]))
router.add("POST", "/api/admin/places", lambda data, params, user: places.create_place(data), auth_required=True, admin_only=True)
router.add("PUT", "/api/admin/places/{id}", lambda data, params, user: places.update_place(params["id"], data), auth_required=True, admin_only=True)
router.add("DELETE", "/api/admin/places/{id}", lambda data, params, user: places.delete_place(params["id"]), auth_required=True, admin_only=True)

# ---- PACKAGES ----
router.add("GET", "/api/packages", lambda data, params, user: packages.list_packages())
router.add("GET", "/api/packages/{id}", lambda data, params, user: packages.get_package(params["id"]))
router.add("POST", "/api/admin/packages", lambda data, params, user: packages.create_package(data), auth_required=True, admin_only=True)
router.add("PUT", "/api/admin/packages/{id}", lambda data, params, user: packages.update_package(params["id"], data), auth_required=True, admin_only=True)
router.add("DELETE", "/api/admin/packages/{id}", lambda data, params, user: packages.delete_package(params["id"]), auth_required=True, admin_only=True)

# ---- BOOKINGS ----
router.add("POST", "/api/bookings", lambda data, params, user: bookings.create_booking(user["id"], data), auth_required=True)
router.add("GET", "/api/bookings/mine", lambda data, params, user: bookings.list_user_bookings(user["id"]), auth_required=True)
router.add("GET", "/api/bookings/{id}", lambda data, params, user: bookings.get_booking(params["id"], user["id"]), auth_required=True)
router.add("GET", "/api/admin/bookings", lambda data, params, user: bookings.list_all_bookings(), auth_required=True, admin_only=True)

# ---- PAYMENT ----
router.add("POST", "/api/payment", lambda data, params, user: payment.pay(user["id"], data), auth_required=True)

# ---- SEARCH ----
router.add("GET", "/api/search", lambda data, params, user: search.search_places(data, user["id"] if user else None))

# ---- CONTACT ----
router.add("POST", "/api/contact", lambda data, params, user: contact.submit_contact(data))
router.add("GET", "/api/admin/contact", lambda data, params, user: contact.list_contact_messages(), auth_required=True, admin_only=True)

# ---- FEEDBACK / REVIEWS ----
router.add("POST", "/api/reviews", lambda data, params, user: feedback.submit_review(user["id"], data), auth_required=True)
router.add("GET", "/api/reviews", lambda data, params, user: feedback.list_reviews(data.get("place_id")))

# ---- NEWS ----
router.add("GET", "/api/news", lambda data, params, user: news.list_news())
router.add("POST", "/api/admin/news", lambda data, params, user: news.create_news(data), auth_required=True, admin_only=True)
router.add("DELETE", "/api/admin/news/{id}", lambda data, params, user: news.delete_news(params["id"]), auth_required=True, admin_only=True)

# ---- GALLERY ----
router.add("GET", "/api/gallery", lambda data, params, user: gallery.list_gallery(data.get("category")))
router.add("POST", "/api/admin/gallery", lambda data, params, user: gallery.add_image(data), auth_required=True, admin_only=True)
router.add("DELETE", "/api/admin/gallery/{id}", lambda data, params, user: gallery.delete_image(params["id"]), auth_required=True, admin_only=True)

# ---- BLOG ----
router.add("GET", "/api/blogs", lambda data, params, user: blog.list_blogs())
router.add("GET", "/api/blogs/{id}", lambda data, params, user: blog.get_blog(params["id"]))
router.add("POST", "/api/blogs", lambda data, params, user: blog.create_blog(user["id"], data), auth_required=True)
router.add("DELETE", "/api/blogs/{id}", lambda data, params, user: blog.delete_blog(params["id"]), auth_required=True)

# ---- PROFILE / DASHBOARD ----
router.add("GET", "/api/dashboard", lambda data, params, user: profile_module.get_dashboard(user["id"]), auth_required=True)
router.add("PUT", "/api/profile", lambda data, params, user: profile_module.update_profile(user["id"], data), auth_required=True)
router.add("POST", "/api/profile/change-password", lambda data, params, user: profile_module.change_password(user["id"], data), auth_required=True)
router.add("POST", "/api/favourites", lambda data, params, user: profile_module.toggle_favourite(user["id"], data), auth_required=True)

# ---- NOTIFICATIONS ----
router.add("GET", "/api/notifications", lambda data, params, user: notifications.list_notifications(user["id"]), auth_required=True)
router.add("POST", "/api/notifications/{id}/read", lambda data, params, user: notifications.mark_read(user["id"], params["id"]), auth_required=True)

# ---- ADMIN: USERS ----
router.add("GET", "/api/admin/users", lambda data, params, user: admin.list_users(), auth_required=True, admin_only=True)
router.add("GET", "/api/admin/users/search", lambda data, params, user: admin.search_users(data.get("q", "")), auth_required=True, admin_only=True)

# ---- REPORTS ----
router.add("GET", "/api/admin/reports/bookings", lambda data, params, user: reports.booking_report(), auth_required=True, admin_only=True)
router.add("GET", "/api/admin/reports/users", lambda data, params, user: reports.user_report(), auth_required=True, admin_only=True)
router.add("GET", "/api/admin/reports/revenue", lambda data, params, user: reports.revenue_report(), auth_required=True, admin_only=True)


# ---------------------------------------------------------------------------
# HTTP REQUEST HANDLER
# ---------------------------------------------------------------------------
class MITourismHandler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def _send_json(self, status, payload):
        self.send_response(status)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json_body_bytes(payload))

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _handle_api(self, method):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        handler, path_params, auth_required, admin_only = router.match(method, path)
        if handler is None:
            self._send_json(404, {"success": False, "message": "API route not found."})
            return

        # Merge query params + path params + JSON body (body wins on conflicts)
        data = dict(query_params)
        data.update(path_params or {})
        if method in ("POST", "PUT", "DELETE"):
            data.update(self._read_json_body())

        token = get_token_from_headers(self)
        user = get_user_from_token(token) if token else None

        if auth_required and not user:
            self._send_json(401, {"success": False, "message": "Authentication required. Please login."})
            return
        if admin_only and (not user or user.get("role") != "admin"):
            self._send_json(403, {"success": False, "message": "Admin access only."})
            return

        try:
            status, payload = handler(data, path_params, user)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            status, payload = 500, {"success": False, "message": f"Server error: {exc}"}

        self._send_json(status, payload)

    # -------------------------------------------------------------------
    # STATIC FILE SERVING (the existing untouched HTML/CSS/JS/images)
    # -------------------------------------------------------------------
    def _serve_static(self):
        parsed = urlparse(self.path)
        rel_path = parsed.path.lstrip("/")
        if rel_path == "":
            rel_path = "HOME.html"

        # URL-decode spaces etc. (e.g. "project INDEX.html")
        from urllib.parse import unquote
        rel_path = unquote(rel_path)

        full_path = os.path.normpath(os.path.join(FRONTEND_DIR, rel_path))
        if not full_path.startswith(FRONTEND_DIR):
            self.send_response(403)
            self.end_headers()
            return

        if not os.path.isfile(full_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        content_type, _ = mimetypes.guess_type(full_path)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self._set_cors_headers()
        self.end_headers()
        with open(full_path, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._handle_api("GET")
        else:
            self._serve_static()

    def do_POST(self):
        self._handle_api("POST")

    def do_PUT(self):
        self._handle_api("PUT")

    def do_DELETE(self):
        self._handle_api("DELETE")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")


def run():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), MITourismHandler)
    print(f"MI Tourism Development backend running at http://localhost:{PORT}")
    print(f"Serving frontend from: {FRONTEND_DIR}")
    print(f"Open http://localhost:{PORT}/HOME.html in your browser.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    run()
