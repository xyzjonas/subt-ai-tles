import type { Cue, Job } from "../api/types";
import { currentLocale, t } from "../i18n";

const TIMESTAMP = /\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}/g;

export const MAX_SRT_MB = 25;
export const MAX_SRT_BYTES = MAX_SRT_MB * 1024 * 1024;

export interface SrtInfo {
  cueCount: number;
}

/** Validates a file as UTF-8 SRT and counts its cues. Throws a user-facing Error. */
export async function parseSrt(file: File): Promise<SrtInfo> {
  if (!file.name.toLowerCase().endsWith(".srt")) throw new Error(t("errors.codes.file_not_srt"));
  if (file.size > MAX_SRT_BYTES) throw new Error(t("errors.codes.file_too_large", { max_mb: MAX_SRT_MB }));

  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
  } catch {
    throw new Error(t("errors.codes.file_not_utf8"));
  }

  const cueCount = text.match(TIMESTAMP)?.length ?? 0;
  if (cueCount === 0) throw new Error(t("translate.file.noTimestamps"));
  return { cueCount };
}

export function formatSize(bytes: number): string {
  return bytes < 1024 * 1024
    ? t("translate.file.size.kb", { n: Math.max(1, Math.round(bytes / 1024)) })
    : t("translate.file.size.mb", { n: (bytes / 1024 / 1024).toLocaleString(currentLocale(), { maximumFractionDigits: 1, minimumFractionDigits: 1 }) });
}

export function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  const ago = new Intl.RelativeTimeFormat(currentLocale(), { style: "short" });
  if (mins < 60) return ago.format(-Math.max(1, mins), "minute");
  if (mins < 1440) return ago.format(-Math.floor(mins / 60), "hour");
  return ago.format(-Math.floor(mins / 1440), "day");
}

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: fileName });
  a.click();
  URL.revokeObjectURL(url);
}

export function formatWhen(iso: string): string {
  const d = new Date(iso);
  const time = d.toLocaleTimeString(currentLocale(), { hour: "2-digit", minute: "2-digit", hour12: false });
  const days = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(iso).setHours(0, 0, 0, 0)) / 86400e3);
  if (days === 0) return t("time.today", { time });
  if (days === 1) return t("time.yesterday", { time });
  return `${d.toLocaleDateString(currentLocale(), { month: "short", day: "numeric" })}, ${time}`;
}

const pad = (n: number, width = 2) => String(n).padStart(width, "0");

/** 14200 -> "00:00:14,200" */
export function formatTimecode(ms: number): string {
  return `${pad(Math.floor(ms / 3600e3))}:${pad(Math.floor(ms / 60e3) % 60)}:${pad(Math.floor(ms / 1000) % 60)},${pad(ms % 1000, 3)}`;
}

/** 2538000 -> "42m 18s" */
export function formatRunningTime(ms: number): string {
  const total = Math.round(ms / 1000);
  const h = Math.floor(total / 3600);
  const m = Math.floor(total / 60) % 60;
  return [h && t("time.hours", { n: h }), t("time.minutes", { n: m }), t("time.seconds", { n: total % 60 })].filter(Boolean).join(" ");
}

/** Characters per second a viewer has to read. */
export function cps(cue: Pick<Cue, "start" | "end" | "target">): number {
  return cue.target.replace(/\s/g, "").length / Math.max(0.001, (cue.end - cue.start) / 1000);
}

export function compileSrt(cues: Cue[]): string {
  return cues.map((c) => `${c.index}\n${formatTimecode(c.start)} --> ${formatTimecode(c.end)}\n${c.target}\n`).join("\n");
}

export function translatedFileName(job: Job): string {
  return job.fileName.replace(/\.srt$/i, `.${job.targetLang}.srt`);
}

export function srtBlob(cues: Cue[]): Blob {
  return new Blob([compileSrt(cues)], { type: "application/x-subrip" });
}
