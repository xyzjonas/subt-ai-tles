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
