import type { PluralForms } from "../../i18n/en";

/** Mirrors the app's CPS_LIMIT: above this a cue is flagged "High CPS". */
export const CPS_LIMIT = 17;

export interface PreviewCue {
  index: number;
  start: number;
  end: number;
  source: string;
  target: string;
  /** Alternative renderings offered when the cue is re-translated. */
  variants?: string[];
  expanded?: boolean;
}

export const PREVIEW_CUES: PreviewCue[] = [
  {
    index: 123,
    start: 491_300,
    end: 494_000,
    source: "Keep your eyes on the road, Ren.",
    target: "Dívej se na cestu, Reno.",
  },
  {
    index: 124,
    start: 494_200,
    end: 496_900,
    source: "Wait, did you hear that engine rumble just now?",
    target: "Počkat, slyšel jsi ten motor?",
    expanded: true,
    variants: [
      "Počkej, slyšel jsi to dunění motoru právě teď?",
      "Počkat, slyšel jsi ten motor?",
      "Hele, slyšels to? Ten motor?",
    ],
  },
  {
    index: 125,
    start: 497_300,
    end: 499_000,
    source: "Yeah. Deep in the tunnel — twin-turbo V8, no doubt.",
    target: "Jo. Hluboko v tunelu — dvouturbo V8, žádná otázka.",
  },
];

const pad = (n: number, width = 2) => String(n).padStart(width, "0");

/** 14200 -> "00:00:14,200" */
export function formatTimecode(ms: number): string {
  return `${pad(Math.floor(ms / 3600e3))}:${pad(Math.floor(ms / 60e3) % 60)}:${pad(Math.floor(ms / 1000) % 60)},${pad(ms % 1000, 3)}`;
}

/** Characters per second a viewer has to read. */
export function cps(text: string, start: number, end: number): number {
  return text.replace(/\s/g, "").length / Math.max(0.001, (end - start) / 1000);
}

export function fmt(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(values[key] ?? ""));
}

export function plural(locale: string, forms: PluralForms, count: number): string {
  const category = new Intl.PluralRules(locale).select(count);
  const form = category === "one" ? forms.one : category === "few" ? (forms.few ?? forms.other) : forms.other;
  return fmt(form, { count: count.toLocaleString(locale) });
}
