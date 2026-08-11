# Documentation

## 1. Technology Stack
- Frontend: HTML, CSS, JavaScript (vanilla, no framework) — matches your original stack
- Backend: Python standard library only (`http.server`) — no Flask/Django
- Database: MySQL (via `mysql-connector-python`)

## 2. Authentication
Dummy, academic-project-appropriate auth (per your requirement #11):
- Passwords hashed with salted SHA-256 (`utils.hash_password`) — not
  bcrypt/production grade, but never stored in plain text.
- Sessions are random tokens stored in the `sessions` table with an
  expiry, sent back to the browser and stored in `localStorage`, then
  attached as `Authorization: Bearer <token>` on every API call
  (`assets/js/api.js`).
- Forgot Password uses a 6-digit OTP stored in `password_resets` with a
  10-minute expiry. Since there's no real email service, the OTP is
  returned directly in the API response and shown on-screen — clearly a
  dummy flow, easy to swap for real SMTP later.

## 3. Feature -> File Map

| Feature | Frontend | Backend |
|---|---|---|
| Dynamic homepage (featured/trending/popular/stats/counters) | `HOME.html` (new section added at the bottom) | `places.py` |
| Login / Register / Forgot Password | `login.html`, `register.html`, `forgot-password.html` | `auth.py` |
| User Dashboard | `dashboard.html` | `profile.py` |
| Booking Module | `booking.html` | `bookings.py` |
| Payment (dummy) | `payment.html` | `payment.py` |
| Admin Panel | `admin.html` | `places.py`, `packages.py`, `admin.py`, `news.py`, `gallery.py`, `reports.py` |
| Search + Filters | `search.html` | `search.py` |
| Contact Us | `contact.html` | `contact.py` |
| Feedback / Reviews | `feedback.html` | `feedback.py` |
| News | `news.html` | `news.py` |
| Gallery | `gallery.html` | `gallery.py` |
| Blog | `blog.html` | `blog.py` |
| Profile / Change Password | `profile.html` | `profile.py` |
| Notifications (dummy) | `dashboard.html` (Notifications tab) | `notifications.py` |
| Reports | `admin.html` (Reports tab) | `reports.py` |

## 4. Database Design (see `database/schema.sql`)

Key relationships:
- `bookings.user_id` -> `users.id`, `bookings.package_id` -> `packages.id`
- `packages.place_id` -> `places.id`
- `payments.booking_id` -> `bookings.id`
- `reviews.user_id` -> `users.id`, `reviews.place_id` -> `places.id`
- `favourites` / `recent_searches` -> `users.id` (dashboard data)
- `sessions.user_id` -> `users.id` (login sessions)
- `password_resets.user_id` -> `users.id` (forgot password OTPs)

All foreign keys use `ON DELETE CASCADE` (or `SET NULL` where the child
record should survive) so the data stays consistent.

## 5. REST API Reference

Base URL: `http://localhost:8000/api`

### Auth
| Method | Path | Body | Auth |
|---|---|---|---|
| POST | `/auth/register` | `full_name, email, phone?, password` | - |
| POST | `/auth/login` | `email, password` | - |
| POST | `/auth/forgot-password` | `email` | - |
| POST | `/auth/reset-password` | `email, otp, new_password` | - |
| POST | `/auth/logout` | - | required |

### Homepage
| GET `/home/featured` | GET `/home/trending-packages` | GET `/home/popular` | GET `/home/stats` |

### Places / Packages
| GET `/places` (query: district, category, min_rating) | GET `/places/{id}` |
| GET `/packages` | GET `/packages/{id}` |
| Admin only: POST/PUT/DELETE `/admin/places[/{id}]`, `/admin/packages[/{id}]` |

### Bookings & Payment
| POST `/bookings` (`package_id, travel_date, members, vehicle_type, hotel_type`) — auth required |
| GET `/bookings/mine` — auth required |
| GET `/bookings/{id}` — auth required |
| GET `/admin/bookings` — admin only |
| POST `/payment` (`booking_id, method, ...method-specific fields`) — auth required |

### Search
| GET `/search?q=&district=&category=&min_rating=&max_budget=` |

### Contact / Feedback / News / Gallery / Blog
| POST `/contact` | GET `/admin/contact` (admin) |
| POST `/reviews` (auth) | GET `/reviews?place_id=` |
| GET `/news` | POST/DELETE `/admin/news[/{id}]` (admin) |
| GET `/gallery?category=` | POST/DELETE `/admin/gallery[/{id}]` (admin) |
| GET `/blogs` | GET `/blogs/{id}` | POST `/blogs` (auth) | DELETE `/blogs/{id}` (auth) |

### Profile / Dashboard / Notifications
| GET `/dashboard` (auth) | PUT `/profile` (auth) | POST `/profile/change-password` (auth) |
| POST `/favourites` (`place_id`) (auth) |
| GET `/notifications` (auth) | POST `/notifications/{id}/read` (auth) |

### Admin: Users & Reports
| GET `/admin/users` | GET `/admin/users/search?q=` |
| GET `/admin/reports/bookings` | GET `/admin/reports/users` | GET `/admin/reports/revenue` |

All responses are JSON: `{"success": true/false, "message": "...", ...}`.

## 6. Code Quality Notes
- Every backend module has a single responsibility (auth, places, bookings,
  etc.) and reuses `db.run_query()` / `utils.py` helpers instead of
  duplicating SQL connection or validation code.
- `server.py`'s `Router` class centralises route -> handler -> auth-required
  mapping in one readable table instead of a long if/elif chain.
- Frontend JS reuses one `apiRequest()` helper (`assets/js/api.js`) across
  every page instead of repeating `fetch()` boilerplate.
- Server-side validation (email/phone format, required fields, price
  recalculated server-side for bookings) backs up the client-side HTML5
  `required`/`pattern` validation, so the API can't be tricked by disabling
  JavaScript.

## 7. Known Simplifications (acceptable for an academic project)
- Password hashing is salted SHA-256, not bcrypt/argon2.
- "Email confirmation" and "OTP" are dummy — returned in the API response
  instead of being sent through a real mail/SMS provider.
- Gallery/profile-picture "uploads" are URL fields, not real binary file
  uploads (no upload endpoint is required by the brief).
- Revenue report only sums `payments` rows already in MySQL — not a real
  accounting system.
