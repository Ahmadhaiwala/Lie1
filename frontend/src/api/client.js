/**
 * api/client.js
 * Base fetch wrapper — all API calls go through here.
 *
 * Reads VITE_API_URL from .env (falls back to http://localhost:8000).
 * Every call returns { data, error, status } so callers never throw.
 */

export const BASE_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Generic fetch wrapper.
 * @param {string} path      - e.g. "/api/v1/leads"
 * @param {RequestInit} opts - standard fetch options
 * @returns {{ data: any, error: string|null, status: number }}
 */
export async function apiFetch(path, opts = {}) {
  const url = `${BASE_URL}${path}`;
  const defaultHeaders = { "Content-Type": "application/json" };

  try {
    const res = await fetch(url, {
      ...opts,
      headers: { ...defaultHeaders, ...(opts.headers || {}) },
    });

    let data = null;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      data = await res.json();
    } else {
      data = await res.text();
    }

    if (!res.ok) {
      const message =
        (data && typeof data === "object" && data.detail) ||
        (typeof data === "string" && data) ||
        `HTTP ${res.status}`;
      return { data: null, error: message, status: res.status };
    }

    return { data, error: null, status: res.status };
  } catch (err) {
    // Network error / backend not running
    return {
      data: null,
      error: err.message || "Network error — is the backend running?",
      status: 0,
    };
  }
}

/** Convenience helpers */
export const apiGet    = (path, opts = {}) => apiFetch(path, { method: "GET",   ...opts });
export const apiPost   = (path, body, opts = {}) =>
  apiFetch(path, { method: "POST",  body: JSON.stringify(body), ...opts });
export const apiPatch  = (path, body, opts = {}) =>
  apiFetch(path, { method: "PATCH", body: JSON.stringify(body), ...opts });

/**
 * Check if the backend is reachable.
 * @returns {Promise<boolean>}
 */
export async function checkBackendHealth() {
  const { data, error } = await apiGet("/health");
  return !error && data?.status === "ok";
}
