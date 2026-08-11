/* =============================================================================
   api.js
   Shared fetch() wrapper used by every new page's JS file.
   Keeps the base URL and auth-token handling in ONE place (DRY / reusable).
   ============================================================================= */

const API_BASE = "http://localhost:8000/api";

const Auth = {
  getToken() { return localStorage.getItem("mitd_token"); },
  setToken(token) { localStorage.setItem("mitd_token", token); },
  clearToken() { localStorage.removeItem("mitd_token"); },
  getUser() {
    const raw = localStorage.getItem("mitd_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(user) { localStorage.setItem("mitd_user", JSON.stringify(user)); },
  isLoggedIn() { return !!this.getToken(); },
  isAdmin() {
    const u = this.getUser();
    return !!u && u.role === "admin";
  },
  logout() {
    this.clearToken();
    localStorage.removeItem("mitd_user");
    window.location.href = "login.html";
  },
};

/**
 * apiRequest - thin wrapper around fetch() that:
 *  - prefixes API_BASE
 *  - attaches the Bearer token automatically when logged in
 *  - always sends/receives JSON
 *  - returns { ok, status, data } instead of throwing, so callers can do
 *    simple `if (!res.ok) showError(res.data.message)` without try/catch.
 */
async function apiRequest(path, { method = "GET", body = null } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
  } catch (err) {
    return {
      ok: false,
      status: 0,
      data: { success: false, message: "Cannot reach the server. Is backend/server.py running?" },
    };
  }
}

/* Small helpers reused across pages */
function showAlert(containerId, message, type = "error") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = message;
  el.style.display = "block";
}

function requireLogin() {
  if (!Auth.isLoggedIn()) {
    window.location.href = "login.html";
  }
}

function requireAdmin() {
  if (!Auth.isLoggedIn() || !Auth.isAdmin()) {
    window.location.href = "login.html";
  }
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
}

function starString(rating) {
  const full = Math.round(rating || 0);
  return "★".repeat(full) + "☆".repeat(5 - full);
}
