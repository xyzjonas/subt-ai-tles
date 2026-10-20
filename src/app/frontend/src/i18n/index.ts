import { createI18n } from "vue-i18n";
import cs from "./locales/cs";
import en from "./locales/en";

export const LOCALES = ["en", "cs"] as const;
export type Locale = (typeof LOCALES)[number];
export type MessageSchema = typeof en;

const STORAGE_KEY = "locale";
const isLocale = (value: string | null): value is Locale => LOCALES.includes(value as Locale);

const browserLocale = (): Locale => (navigator.languages.some((l) => l.toLowerCase().startsWith("cs")) ? "cs" : "en");

function initialLocale(): Locale {
  const stored = localStorage.getItem(STORAGE_KEY);
  return isLocale(stored) ? stored : browserLocale();
}

/** Czech has three plural forms: 1, 2-4 and the rest (0 and 5+). */
const czechPlural = (choice: number, length: number) => {
  if (length < 3) return choice === 1 ? 0 : 1;
  if (choice === 1) return 0;
  return choice >= 2 && choice <= 4 ? 1 : 2;
};

export const i18n = createI18n<[MessageSchema], Locale, false>({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: "en",
  messages: { en, cs },
  pluralRules: { cs: czechPlural },
});

const composer = i18n.global;
export const t = composer.t;
export const te = composer.te;

document.documentElement.lang = composer.locale.value;

export function setLocale(locale: Locale) {
  composer.locale.value = locale;
  localStorage.setItem(STORAGE_KEY, locale);
  document.documentElement.lang = locale;
}

/** Forgets the stored choice and follows the browser's language again. */
export function resetLocale() {
  localStorage.removeItem(STORAGE_KEY);
  composer.locale.value = browserLocale();
  document.documentElement.lang = composer.locale.value;
}

/** BCP 47 tag of the active locale, for Intl and toLocale*String. */
export const currentLocale = (): Locale => composer.locale.value;
