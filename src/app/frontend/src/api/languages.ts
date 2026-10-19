import { requestJson } from "./http";
import type { Language } from "./types";

/** GET /api/languages */
export function listLanguages(): Promise<Language[]> {
  return requestJson("/languages");
}

/** POST /api/subtitles/detect-language (multipart: file) -> language code */
export async function detectLanguage(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const { code } = await requestJson<{ code: string }>("/subtitles/detect-language", { method: "POST", body: form });
  return code;
}
