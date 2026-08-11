# MI Tourism Development — Full Stack Project

Your original frontend (`HOME.html`, `project INDEX.html`, `MI HTML CSS JS
PROJECT.html`, and all images) is **untouched** — same design, same colors
(`#1abc9c` teal / `#333` navbar), same fonts, same layout. This project only
**adds** a Python + MySQL backend and new pages behind the scenes.

## Folder Structure

```
MI_TOURISM_FULLSTACK/
├── frontend/                  # Your original site + new pages
│   ├── HOME.html              # UNCHANGED design (only a util-bar + dynamic
│   │                          #   section were ADDED, nothing removed/edited)
│   ├── project INDEX.html     # UNCHANGED design (util-bar added)
│   ├── MI HTML CSS JS PROJECT.html   # UNCHANGED, untouched
│   ├── login.html             # NEW
│   ├── register.html          # NEW
│   ├── forgot-password.html   # NEW
│   ├── dashboard.html         # NEW - user dashboard
│   ├── booking.html           # NEW - package booking
│   ├── payment.html           # NEW - dummy payment
│   ├── admin.html             # NEW - admin panel
│   ├── search.html            # NEW - search & filter
│   ├── contact.html           # NEW
│   ├── feedback.html          # NEW
│   ├── news.html              # NEW
│   ├── gallery.html           # NEW
│   ├── blog.html              # NEW
│   ├── profile.html           # NEW
│   └── assets/
│       ├── css/common.css     # Shared styles for new pages (same color theme)
│       ├── js/api.js          # Shared fetch()/auth helper used by every new page
│       └── img/                # Copy of your images (originals also kept in
│                                #  frontend/ root so old HOML.html paths still work)
├── backend/
│   ├── server.py               # Entry point (pure Python http.server, no framework)
│   ├── db.py                   # MySQL connection pool
│   ├── utils.py                # Password hashing, sessions, validation helpers
│   ├── auth.py                 # Login / Register / Forgot Password
│   ├── places.py                # Tourist places CRUD + homepage dynamic data
│   ├── packages.py              # Tour package CRUD
│   ├── bookings.py              # Booking creation & retrieval
│   ├── payment.py               # Dummy payment gateway
│   ├── search.py                # Search + filters
│   ├── contact.py               # Contact form storage
│   ├── feedback.py              # Reviews/ratings
│   ├── news.py                  # Tourism news CRUD
│   ├── gallery.py               # Gallery image CRUD
│   ├── blog.py                  # Travel blog CRUD
│   ├── profile.py               # Dashboard, profile edit, favourites
│   ├── notifications.py         # Dummy notifications
│   ├── admin.py                 # User search/listing for admin
│   ├── reports.py               # Booking / user / revenue reports
│   └── requirements.txt
├── database/
│   └── schema.sql               # Full MySQL schema + seed data
└── docs/
    └── DOCUMENTATION.md
```

## Setup

### 1. MySQL

```bash
mysql -u root -p < database/schema.sql
```

This creates the `mi_tourism_db` database, all tables (with primary/foreign
keys), and some demo places/packages/news/stats so the site isn't empty on
first run.

### 2. Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv
```

Open `backend/db.py` and set your real MySQL password in `DB_CONFIG`.

```bash
python server.py
```

You should see:
```
MI Tourism Development backend running at http://localhost:8000
Open http://localhost:8000/HOME.html in your browser.
```

### 3. Open the site

Go to **http://localhost:8000/HOME.html** — the backend server serves your
existing frontend files directly, so there's no separate frontend server
needed, and no CORS issues.

(You can also just double-click `HOME.html` to open it via `file://`, but
then set `API_BASE` in `frontend/assets/js/api.js` to
`http://localhost:8000/api` — it already is by default — and keep
`backend/server.py` running in another terminal.)

### 4. Login as admin

A demo admin account is seeded in `schema.sql`
(`admin@mitourism.com`). Since the seeded password hash is a placeholder,
**register a new account first**, then in MySQL run:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-registered-email@example.com';
```

Then log in again and you'll be sent to `admin.html` instead of
`dashboard.html`.

## What was NOT changed

- HOME.html / project INDEX.html layout, colors, fonts, navbar — identical
  to your upload.
- No existing file was renamed or deleted.
- All original images/video are still in `frontend/` at their original
  relative paths (they're also duplicated into `frontend/assets/img/` for
  the new pages to use).

## What was added

See `docs/DOCUMENTATION.md` for the full feature-by-feature breakdown and
the REST API reference.
