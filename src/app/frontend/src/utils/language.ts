import type { Language } from "../api/types";
import type { Locale } from "../i18n";

/** Flag shown for a UI language. */
export const LOCALE_FLAGS: Record<Locale, string> = { en: "🇬🇧", cs: "🇨🇿" };

/** Upper-cased language code, `?` while the language is not known yet. */
export const languageCode = (code?: string | null): string => code?.toUpperCase() ?? "?";

/** Name of a language code in the UI language, e.g. `cs` -> `Czech` / `čeština`. */
export function displayLanguage(code: string, locale: string): string | undefined {
  try {
    return new Intl.DisplayNames([locale], { type: "language" }).of(code);
  } catch {
    return undefined;
  }
}

/** Language name in the UI language (`Intl.DisplayNames`), falling back to the backend's name. */
export function languageName(language: Language, locale: string): string {
  return displayLanguage(language.code, locale) ?? language.name;
}

/** `🇨🇿 Czech (čeština)`: the native name is only added when it differs. */
export function languageLabel(language: Language, locale: string): string {
  const name = languageName(language, locale);
  const native = language.native && language.native.toLowerCase() !== name.toLowerCase() ? ` (${language.native})` : "";
  return `${language.flag} ${name}${native}`;
}
