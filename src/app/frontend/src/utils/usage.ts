import type { UsageKind } from "../api/types";

export type UsagePeriod = "day" | "week" | "month";

const number = new Intl.NumberFormat("en", { maximumFractionDigits: 2 });

export const formatCredits = (credits: number) => number.format(credits);
export const formatTokens = (tokens: number) => tokens.toLocaleString("en");

export const KIND_LABEL: Record<UsageKind, string> = {
  translate: "Translation",
  retranslate: "Retranslate cue",
  summarize: "Story summary",
};

/** `start` is a plain `YYYY-MM-DD`; parse it as a local date so it never shifts a day. */
const asLocalDate = (start: string) => new Date(`${start}T00:00:00`);

export function periodLabel(start: string, period: UsagePeriod): string {
  const date = asLocalDate(start);
  if (period === "month") return date.toLocaleDateString("en", { month: "long", year: "numeric" });
  const day = date.toLocaleDateString("en", { month: "short", day: "numeric" });
  return period === "week" ? `Week of ${day}` : day;
}
