/**
 * api/jobs.js
 * Job trigger + status polling API calls.
 */
import { apiGet, apiPost } from "./client";

/**
 * Trigger a new lead generation run.
 * @param {{ service?: string, services?: string[], min_score?: number }} body
 * @returns {{ data: { job_id, status, message }, error: string|null }}
 */
export async function runJob(body = {}) {
  return apiPost("/api/v1/jobs/run", {
    service:   body.service   || null,
    services:  body.services  || null,
    min_score: body.min_score ?? 0.5,
  });
}

/**
 * Fetch the current status of a job.
 * @param {string} jobId
 * @returns {{ data: JobRecord, error: string|null }}
 */
export async function fetchJobStatus(jobId) {
  return apiGet(`/api/v1/jobs/${jobId}/status`);
}

/**
 * List all job records.
 * @returns {{ data: JobRecord[], error: string|null }}
 */
export async function fetchAllJobs() {
  return apiGet("/api/v1/jobs");
}

/**
 * Configure a recurring schedule.
 * @param {{ mode, hour?, minute?, day_of_week?, hours?, cron_expr?, service?, min_score? }} body
 */
export async function scheduleJob(body) {
  return apiPost("/api/v1/jobs/schedule", body);
}

/**
 * Poll a job until it reaches done/failed or timeout.
 * Calls onUpdate(jobRecord) on every poll.
 *
 * @param {string} jobId
 * @param {(record: object) => void} onUpdate
 * @param {{ intervalMs?: number, timeoutMs?: number }} options
 * @returns {Promise<object>} final job record
 */
export async function pollJobUntilDone(jobId, onUpdate, { intervalMs = 1500, timeoutMs = 600000 } = {}) {
  const deadline = Date.now() + timeoutMs;

  return new Promise((resolve, reject) => {
    const tick = async () => {
      if (Date.now() > deadline) {
        reject(new Error("Job polling timed out"));
        return;
      }

      const { data, error } = await fetchJobStatus(jobId);

      if (error) {
        // Backend unreachable — keep trying
        setTimeout(tick, intervalMs * 2);
        return;
      }

      if (typeof onUpdate === "function") onUpdate(data);

      if (data.status === "done" || data.status === "failed") {
        resolve(data);
      } else {
        setTimeout(tick, intervalMs);
      }
    };

    tick();
  });
}
