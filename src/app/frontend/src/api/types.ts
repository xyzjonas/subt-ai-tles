import type { Locale } from "../i18n";

export interface Language {
  code: string;
  name: string;
  native?: string;
  flag: string;
}

export type JobStatus = "processing" | "ready" | "failed";
/** Where a processing job is; `recognizing` also covers waiting in the queue. */
export type JobStage = "recognizing" | "summarizing" | "translating";
/** What happened to the story brief of the title. */
export type SummaryStatus = "generated" | "stored" | "skipped" | "failed";

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
  /** Current pipeline stage (processing jobs). */
  stage?: JobStage;
  /** Outcome of the story brief, once known. */
  summaryStatus?: SummaryStatus;
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

export interface CurrentUser {
  id: number;
  username: string;
  isAdmin: boolean;
  /** False for blocked users. */
  isActive: boolean;
  /** True while the password is a temporary one an admin set. */
  mustChangePassword: boolean;
  /** Credits per calendar month (UTC). */
  monthlyQuota: number;
  /** UI language; null follows the browser. */
  locale: Locale | null;
  createdAt: string;
}

/** Fields an admin can change on any user; omitted ones stay as they are. */
export interface UserUpdate {
  /** Sets a temporary password the user must replace on their next sign-in. */
  password?: string;
  isActive?: boolean;
  monthlyQuota?: number;
}

export interface NewUser {
  username: string;
  /** Temporary: the user must replace it on first sign-in. */
  password: string;
  isAdmin: boolean;
  monthlyQuota?: number;
  locale?: Locale | null;
}

export type UsageKind = "translate" | "retranslate" | "summarize";

export interface UsageRecord {
  id: number;
  kind: UsageKind;
  model: string;
  /** Null once the job was deleted or cancelled. */
  jobId: string | null;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  credits: number;
  createdAt: string;
}

/** Usage of one day, week (starting Monday) or month. */
export interface UsageBucket {
  /** First day of the period, `YYYY-MM-DD`. */
  start: string;
  requests: number;
  tokens: number;
  credits: number;
}

export interface Quota {
  limit: number;
  used: number;
  remaining: number;
}

/** Buckets are oldest first and include empty periods. */
export interface UsageSummary {
  quota: Quota;
  daily: UsageBucket[];
  weekly: UsageBucket[];
  monthly: UsageBucket[];
}

export interface ModelOption {
  id: string;
  label: string;
  /** Plain-language explanation shown on the model card. */
  description: string;
  /** False for models that manage their own randomness (temperature is ignored). */
  supportsTemperature: boolean;
  /** Credits charged per 1,000 prompt / completion tokens. */
  inputCreditsPer1K: number;
  outputCreditsPer1K: number;
}

/** Global translation settings (admin). */
export interface AppSettings {
  model: string;
  /** 0 (literal, consistent) to 1 (creative, varied). */
  temperature: number;
  /** The curated models an admin can choose from. */
  models: ModelOption[];
}

export type AppSettingsUpdate = Pick<AppSettings, "model" | "temperature">;
