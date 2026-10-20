import type { UsageKind } from "../api/types";
import { currentLocale, t } from "../i18n";

export type UsagePeriod = "day" | "week" | "month";

export const formatCredits = (credits: number) => credits.toLocaleString(currentLocale(), { maximumFractionDigits: 2 });
export const formatTokens = (tokens: number) => tokens.toLocaleString(currentLocale());

export const kindLabel = (kind: UsageKind) => t(`dashboard.records.kind.${kind}`);

/** `start` is a plain `YYYY-MM-DD`; parse it as a local date so it never shifts a day. */
const asLocalDate = (start: string) => new Date(`${start}T00:00:00`);

export function periodLabel(start: string, period: UsagePeriod): string {
  const date = asLocalDate(start);
  const locale = currentLocale();
  if (period === "month") return date.toLocaleDateString(locale, { month: "long", year: "numeric" });
  const day = date.toLocaleDateString(locale, { month: "short", day: "numeric" });
  return period === "week" ? t("dashboard.summary.weekOf", { day }) : day;
}
