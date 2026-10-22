export const REPO_URL = "https://github.com/xyzjonas/subt-ai-tles";
export const RELEASES_URL = `${REPO_URL}/releases`;
export const LICENSE_URL = `${REPO_URL}/blob/main/LICENSE`;

export const LOCALES = ["en", "cs"] as const;
export type Locale = (typeof LOCALES)[number];

/** Prefix a site-absolute path with the configured `base` (e.g. `/subt-ai-tles`). */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}${path}`;
}

export function localePath(locale: Locale): string {
  return withBase(locale === "en" ? "/" : `/${locale}/`);
}

export const QUICKSTART_COMMAND = [
  `git clone ${REPO_URL}.git && cd subt-ai-tles`,
  "printf 'OPENAI_API_KEY=sk-...\\nTMDB_API_KEY=...\\n' > .env",
  "docker compose up -d --build",
];
