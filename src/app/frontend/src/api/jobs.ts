import { delay } from "./stub";
import type { CreateJobPayload, Job, JobEstimate } from "./types";

const JOBS: Job[] = [
  { id: "job_0", fileName: "tokyo_midnight_run_part1.srt", sourceLang: "en", targetLang: "ja", cueCount: 750, processedCues: 512, step: "AI translation engine translating chunk #7", createdAt: new Date(Date.now() - 2 * 60e3).toISOString(), status: "processing" },
  { id: "job_1", fileName: "the_last_voyage_s01e03.srt", sourceLang: "en", targetLang: "es", cueCount: 1204, createdAt: new Date(Date.now() - 2 * 3600e3).toISOString(), status: "ready", model: "GPT-4o", confidence: 99.4 },
  { id: "job_2", fileName: "neon_district_ep12.srt", sourceLang: "ja", targetLang: "en", cueCount: 968, createdAt: new Date(Date.now() - 26 * 3600e3).toISOString(), status: "ready", model: "GPT-4o" },
  { id: "job_3", fileName: "documentary_cut_final.srt", sourceLang: "en", targetLang: "de", cueCount: 512, createdAt: new Date(Date.now() - 3 * 86400e3).toISOString(), status: "ready", model: "GPT-4o" },
];

const CUES_PER_SECOND = 8;
const lastTick = new Map<string, number>();

/** Stub only: simulates the backend translating cues in the background. */
function advance(job: Job) {
  if (job.status !== "processing") return;
  const now = Date.now();
  const elapsed = (now - (lastTick.get(job.id) ?? now)) / 1000;
  lastTick.set(job.id, now);
  job.processedCues = Math.min(job.cueCount, (job.processedCues ?? 0) + elapsed * CUES_PER_SECOND);
  if (job.processedCues >= job.cueCount) Object.assign(job, { status: "ready", model: "GPT-4o" });
}

/** GET /api/jobs?limit=n */
export function listJobs(limit?: number): Promise<Job[]> {
  JOBS.forEach(advance);
  return delay((limit ? JOBS.slice(0, limit) : JOBS).map((j) => ({ ...j, processedCues: j.processedCues && Math.floor(j.processedCues) })));
}

/** GET /api/jobs/:id (polled while processing) */
export async function getJob(id: string): Promise<Job> {
  const found = (await delay(JOBS)).find((j) => j.id === id);
  if (found) advance(found);
  const job = found && { ...found, processedCues: found.processedCues && Math.floor(found.processedCues) };
  if (!job) throw new Error("Job not found");
  return job;
}

/** POST /api/jobs/estimate  { cueCount } */
export function estimateJob(cueCount: number): Promise<JobEstimate> {
  return delay({ seconds: Math.max(5, Math.round(cueCount / 24)), tokens: cueCount * 5 }, 150);
}

/** POST /api/jobs (multipart) -> 201 { id } */
export function createJob(_payload: CreateJobPayload): Promise<{ id: string }> {
  return delay({ id: `job_${Date.now()}` }, 600);
}

/** GET /api/jobs/:id/download -> translated .srt */
export function downloadJob(job: Job): Promise<Blob> {
  const body = `1\n00:00:01,000 --> 00:00:03,000\n[${job.targetLang.toUpperCase()}] ${job.fileName}\n`;
  return delay(new Blob([body], { type: "application/x-subrip" }), 200);
}

/** DELETE /api/jobs/:id/translation — stops a processing job */
export async function cancelJob(id: string): Promise<void> {
  await delay(null, 300);
  const i = JOBS.findIndex((j) => j.id === id);
  if (i >= 0) JOBS.splice(i, 1);
}
