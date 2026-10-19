import { delay } from "./stub";
import type { Language } from "./types";

/** ISO 639-1 language code -> ISO 3166-1 country whose flag represents it. */
const FLAGS: Record<string, string> = {
  en: "GB", es: "ES", ja: "JP", de: "DE", fr: "FR", it: "IT", pt: "PT", ko: "KR",
  zh: "CN", ru: "RU", ar: "SA", hi: "IN", bn: "BD", ur: "PK", tr: "TR", nl: "NL",
  pl: "PL", uk: "UA", cs: "CZ", sk: "SK", sv: "SE", da: "DK", no: "NO", fi: "FI",
  is: "IS", el: "GR", he: "IL", fa: "IR", th: "TH", vi: "VN", id: "ID", ms: "MY",
  tl: "PH", hu: "HU", ro: "RO", bg: "BG", sr: "RS", hr: "HR", sl: "SI", bs: "BA",
  mk: "MK", sq: "AL", et: "EE", lv: "LV", lt: "LT", ka: "GE", hy: "AM", az: "AZ",
  kk: "KZ", uz: "UZ", mn: "MN", ne: "NP", si: "LK", my: "MM", km: "KH", lo: "LA",
  sw: "KE", am: "ET", af: "ZA", ga: "IE", mt: "MT", lb: "LU", be: "BY", ca: "AD",
};

const flagEmoji = (country: string) =>
  String.fromCodePoint(...[...country].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));

const english = new Intl.DisplayNames("en", { type: "language" });

const LANGUAGES: Language[] = Object.entries(FLAGS)
  .map(([code, country]) => {
    const name = english.of(code) ?? code;
    const native = new Intl.DisplayNames(code, { type: "language" }).of(code);
    return { code, name, native: native && native !== name ? native : undefined, flag: flagEmoji(country) };
  })
  .sort((a, b) => a.name.localeCompare(b.name));

/** GET /api/languages */
export function listLanguages(): Promise<Language[]> {
  return delay(LANGUAGES, 100);
}

/** POST /api/subtitles/detect-language (multipart: file) */
export function detectLanguage(_file: File): Promise<string> {
  return delay("en", 400);
}
