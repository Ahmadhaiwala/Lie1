/**
 * api/leads.js
 * All lead-related API calls.
 */
import { apiGet, apiPatch } from "./client";

/**
 * Fetch all leads with optional filters.
 * @param {{ service?, tier?, q?, limit?, offset? }} params
 * @returns {{ data: Lead[], error: string|null }}
 */
export async function fetchLeads(params = {}) {
  const qs = new URLSearchParams();
  if (params.service) qs.set("service", params.service);
  if (params.tier)    qs.set("tier",    params.tier);
  if (params.q)       qs.set("q",       params.q);
  if (params.limit)   qs.set("limit",   params.limit);
  if (params.offset)  qs.set("offset",  params.offset);

  const query = qs.toString() ? `?${qs.toString()}` : "";
  return apiGet(`/api/v1/leads${query}`);
}

/**
 * Fetch aggregate stats (total, hot, warm, cold, by_service).
 * @returns {{ data: Stats, error: string|null }}
 */
export async function fetchLeadStats() {
  return apiGet("/api/v1/leads/stats");
}

/**
 * Fetch a single lead by ID.
 * @param {string} leadId
 */
export async function fetchLead(leadId) {
  return apiGet(`/api/v1/leads/${leadId}`);
}

/**
 * Mark a lead's outreach as sent (or update notes).
 * @param {string} leadId
 * @param {{ outreach_sent?: boolean, notes?: string }} fields
 */
export async function updateLead(leadId, fields) {
  return apiPatch(`/api/v1/leads/${leadId}`, fields);
}
