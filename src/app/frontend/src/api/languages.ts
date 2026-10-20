import { requestJson } from "./http";
import type { Language } from "./types";

/** GET /api/languages */
export function listLanguages(): Promise<Language[]> {
  return requestJson("/languages");
}
