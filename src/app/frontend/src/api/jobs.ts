import { request, requestJson } from "./http";
import type { CreateJobPayload, Job, JobEstimate } from "./types";

/** GET /api/jobs?limit=n */
export function listJobs(limit?: number): Promise<Job[]> {
  return requestJson(limit ? `/jobs?limit=${limit}` : "/jobs");
}

/** GET /api/jobs/:id (polled while processing) */
export function getJob(id: string): Promise<Job> {
  return requestJson(`/jobs/${id}`);
}

/** POST /api/jobs/estimate  { cueCount } */
export function estimateJob(cueCount: number): Promise<JobEstimate> {
  return requestJson("/jobs/estimate", { method: "POST", body: { cueCount } });
}

/** POST /api/jobs (multipart) -> 201 the created job */
export function createJob({ file, sourceLang, targetLang }: CreateJobPayload): Promise<Job> {
  const form = new FormData();
  form.append("file", file);
  form.append("sourceLang", sourceLang);
  form.append("targetLang", targetLang);
  return requestJson("/jobs", { method: "POST", body: form });
}

/** GET /api/jobs/:id/download -> translated .srt */
export async function downloadJob(job: Job): Promise<Blob> {
  return (await request(`/jobs/${job.id}/download`)).blob();
}

/** DELETE /api/jobs/:id/translation — stops a processing job */
export async function cancelJob(id: string): Promise<void> {
  await request(`/jobs/${id}/translation`, { method: "DELETE" });
}
