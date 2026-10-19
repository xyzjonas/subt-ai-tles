import type { Cue, Job } from "../api/types";

const TIMESTAMP = /\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}/g;

export const MAX_SRT_BYTES = 25 * 1024 * 1024;

export interface SrtInfo {
  cueCount: number;
}

/** Validates a file as UTF-8 SRT and counts its cues. Throws a user-facing Error. */
export async function parseSrt(file: File): Promise<SrtInfo> {
  if (!file.name.toLowerCase().endsWith(".srt")) throw new Error("Only .srt files are supported.");
  if (file.size > MAX_SRT_BYTES) throw new Error("File exceeds the 25MB limit.");

  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
  } catch {
    throw new Error("File must be UTF-8 encoded.");
  }

  const cueCount = text.match(TIMESTAMP)?.length ?? 0;
  if (cueCount === 0) throw new Error("No valid SRT timestamps found.");
  return { cueCount };
}

export function formatSize(bytes: number): string {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${Math.max(1, mins)}m ago`;
  if (mins < 1440) return `${Math.floor(mins / 60)}h ago`;
  return `${Math.floor(mins / 1440)}d ago`;
}

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: fileName });
  a.click();
  URL.revokeObjectURL(url);
}

export function formatWhen(iso: string): string {
  const d = new Date(iso);
  const time = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
  const days = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(iso).setHours(0, 0, 0, 0)) / 86400e3);
  if (days === 0) return `Today, ${time}`;
  if (days === 1) return `Yesterday, ${time}`;
  return `${d.toLocaleDateString([], { month: "short", day: "numeric" })}, ${time}`;
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
  return [h && `${h}h`, `${m}m`, `${total % 60}s`].filter(Boolean).join(" ");
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
