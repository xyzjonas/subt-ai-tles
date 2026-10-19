import { request } from "./http";
import { basicHeader, saveSession } from "./session";

/** Verifies the credentials against GET /api/auth/me, then keeps them for later requests. */
export async function login(username: string, password: string): Promise<void> {
  const header = basicHeader(username, password);
  await request("/auth/me", { headers: { Authorization: header }, redirectOnUnauthorized: false });
  saveSession(header);
}
