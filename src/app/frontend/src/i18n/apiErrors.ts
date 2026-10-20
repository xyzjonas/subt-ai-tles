import { ApiError } from "../api/http";
import { t, te } from ".";

const STATUS_KEYS: [(status: number) => boolean, string][] = [
  [(s) => s === 401, "errors.http401"],
  [(s) => s === 403, "errors.http403"],
  [(s) => s === 404, "errors.http404"],
  [(s) => s === 413, "errors.http413"],
  [(s) => s === 422, "errors.http422"],
  [(s) => s === 429, "errors.http429"],
  [(s) => s >= 500, "errors.http5xx"],
];

/**
 * Localized message for a backend error code (also what a failed job stores in `error`).
 * Falls back to the raw text, which is all rows written before error codes have.
 */
export function describeCode(code: string, params: Record<string, string | number> = {}): string {
  const key = `errors.codes.${code}`;
  return te(key) ? t(key, params) : code;
}

/** Message for anything thrown by an API call; `fallbackKey` covers the unexpected. */
export function describeError(error: unknown, fallbackKey: string): string {
  if (error instanceof ApiError) {
    if (error.code && te(`errors.codes.${error.code}`)) return describeCode(error.code, error.params);
    const byStatus = STATUS_KEYS.find(([matches]) => matches(error.status));
    if (byStatus) return t(byStatus[1]);
  } else if (error instanceof TypeError) {
    return t("errors.network"); // fetch rejects with a TypeError when the server is unreachable
  }
  return t(fallbackKey);
}
