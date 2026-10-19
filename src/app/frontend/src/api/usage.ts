import { requestJson } from "./http";
import type { UsageRecord, UsageSummary } from "./types";

/** GET /api/usage -> quota and daily / weekly / monthly summaries */
export function getUsage(): Promise<UsageSummary> {
  return requestJson("/usage");
}

/** GET /api/usage/records?limit=n&offset=m -> one row per request, newest first */
export function listUsageRecords(limit: number, offset: number): Promise<UsageRecord[]> {
  return requestJson(`/usage/records?limit=${limit}&offset=${offset}`);
}
