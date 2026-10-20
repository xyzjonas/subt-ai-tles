import { requestJson } from "./http";
import type { UsageRecord, UsageSummary } from "./types";

/** `/usage` for yourself, `/admin/users/:id/usage` for any user (admin only). */
const base = (userId?: number) => (userId === undefined ? "/usage" : `/admin/users/${userId}/usage`);

/** GET /api/usage -> quota and daily / weekly / monthly summaries */
export function getUsage(userId?: number): Promise<UsageSummary> {
  return requestJson(base(userId));
}

/** GET /api/usage/records?limit=n&offset=m -> one row per request, newest first */
export function listUsageRecords(limit: number, offset: number, userId?: number): Promise<UsageRecord[]> {
  return requestJson(`${base(userId)}/records?limit=${limit}&offset=${offset}`);
}
