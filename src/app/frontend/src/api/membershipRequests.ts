import { request, requestJson } from "./http";
import type { CurrentUser, MembershipRequest, MembershipRequestStatus } from "./types";

/** POST /api/membership-requests (public). The answer is the same whether or not anything was stored. */
export async function submitMembershipRequest(email: string, details: string): Promise<void> {
  await request("/membership-requests", { method: "POST", body: { email, details: details.trim() || null }, redirectOnUnauthorized: false });
}

/** GET /api/admin/membership-requests -> newest first (admin only) */
export function listMembershipRequests(status?: MembershipRequestStatus): Promise<MembershipRequest[]> {
  return requestJson(`/admin/membership-requests${status ? `?status=${status}` : ""}`);
}

/** POST /api/admin/membership-requests/:id/approve -> the new user, with `password` as their temporary one (admin only) */
export function approveMembershipRequest(id: number, password: string): Promise<CurrentUser> {
  return requestJson(`/admin/membership-requests/${id}/approve`, { method: "POST", body: { password } });
}

/** POST /api/admin/membership-requests/:id/reject (admin only) */
export function rejectMembershipRequest(id: number): Promise<MembershipRequest> {
  return requestJson(`/admin/membership-requests/${id}/reject`, { method: "POST" });
}
