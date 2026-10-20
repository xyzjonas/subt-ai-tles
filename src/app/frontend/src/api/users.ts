import { requestJson } from "./http";
import type { CurrentUser, NewUser, UserUpdate } from "./types";

/** GET /api/admin/users -> every user, by username (admin only) */
export function listUsers(): Promise<CurrentUser[]> {
  return requestJson("/admin/users");
}

/** POST /api/admin/users (admin only) */
export function createUser(user: NewUser): Promise<CurrentUser> {
  return requestJson("/admin/users", { method: "POST", body: user });
}

/** PATCH /api/admin/users/:id -> the updated user (admin only) */
export function updateUser(id: number, update: UserUpdate): Promise<CurrentUser> {
  return requestJson(`/admin/users/${id}`, { method: "PATCH", body: update });
}
