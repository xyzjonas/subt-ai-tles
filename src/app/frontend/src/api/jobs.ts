import { delay } from "./stub";
import type { CreateJobPayload, Job, JobEstimate } from "./types";

const JOBS: Job[] = [
  { id: "job_1", fileName: "the_last_voyage_s01e03.srt", sourceLang: "en", targetLang: "es", cueCount: 1204, createdAt: new Date(Date.now() - 2 * 3600e3).toISOString(), status: "ready" },
  { id: "job_2", fileName: "neon_district_ep12.srt", sourceLang: "ja", targetLang: "en", cueCount: 968, createdAt: new Date(Date.now() - 26 * 3600e3).toISOString(), status: "ready" },
  { id: "job_3", fileName: "documentary_cut_final.srt", sourceLang: "en", targetLang: "de", cueCount: 512, createdAt: new Date(Date.now() - 3 * 86400e3).toISOString(), status: "ready" },
];

/** GET /api/jobs?limit=n */
export function listJobs(limit?: number): Promise<Job[]> {
  return delay(limit ? JOBS.slice(0, limit) : JOBS);
}

/** POST /api/jobs/estimate  { cueCount } */
export function estimateJob(cueCount: number): Promise<JobEstimate> {
  return delay({ seconds: Math.max(5, Math.round(cueCount / 24)), tokens: cueCount * 5 }, 150);
}

/** POST /api/jobs (multipart) -> 201 { id } */
export function createJob(_payload: CreateJobPayload): Promise<{ id: string }> {
  return delay({ id: `job_${Date.now()}` }, 600);
}
