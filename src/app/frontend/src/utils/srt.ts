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
