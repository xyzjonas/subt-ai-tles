export interface Language {
  code: string;
  name: string;
  native?: string;
  flag: string;
}

export type JobStatus = "processing" | "ready" | "failed";

export interface Job {
  id: string;
  fileName: string;
  sourceLang: string;
  targetLang: string;
  cueCount: number;
  createdAt: string;
  status: JobStatus;
  /** Cues translated so far (processing jobs). */
  processedCues?: number;
  /** Live pipeline step description (processing jobs). */
  step?: string;
  /** Model the job was synced with (completed jobs). */
  model?: string;
  /** Model confidence 0-100 (completed jobs). */
  confidence?: number;
  /** Why the job failed (failed jobs). */
  error?: string;
}

export interface JobEstimate {
  seconds: number;
  tokens: number;
}

export interface CreateJobPayload {
  file: File;
  sourceLang: string;
  targetLang: string;
}

export interface Cue {
  /** 1-based position in the .srt file. */
  index: number;
  /** Start / end offsets in milliseconds. */
  start: number;
  end: number;
  source: string;
  target: string;
}

export interface CueVariant {
  label: string;
  text: string;
}
