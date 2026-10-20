import { request, requestJson } from "./http";
import type { Locale } from "../i18n";
import type { CurrentUser } from "./types";
import { basicHeader, saveSession } from "./session";

/** Verifies the credentials against GET /api/auth/me, then keeps them for later requests. */
export async function login(username: string, password: string): Promise<void> {
  const header = basicHeader(username, password);
  await request("/auth/me", { headers: { Authorization: header }, redirectOnUnauthorized: false });
  saveSession(header);
}

/** GET /api/auth/me */
export function getCurrentUser(): Promise<CurrentUser> {
  return requestJson("/auth/me");
}

/** PATCH /api/auth/me -> the updated user; `null` makes the app follow the browser's language. */
export function updateProfile(locale: Locale | null): Promise<CurrentUser> {
  return requestJson("/auth/me", { method: "PATCH", body: { locale } });
}

/**
 * POST /api/auth/password. The session is keyed by the password, so on success it is
 * replaced with one for the new password (the old one no longer works).
 */
export async function changePassword(username: string, currentPassword: string, newPassword: string): Promise<void> {
  await request("/auth/password", { method: "POST", body: { currentPassword, newPassword } });
  saveSession(basicHeader(username, newPassword));
}
