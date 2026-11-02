import { ref, watch } from "vue";
import { approveMembershipRequest, listMembershipRequests, rejectMembershipRequest } from "../api/membershipRequests";
import type { CurrentUser, MembershipRequest, MembershipRequestStatus } from "../api/types";
import { t } from "../i18n";
import { describeError } from "../i18n/apiErrors";

/** Membership requests of one status, and the admin decisions on them. Decisions resolve to an error message, or "" on success. */
export function useMembershipRequests() {
  const status = ref<MembershipRequestStatus>("pending");
  const requests = ref<MembershipRequest[]>([]);
  const loading = ref(true);
  const error = ref("");

  async function load() {
    loading.value = true;
    error.value = "";
    const wanted = status.value;
    try {
      const rows = await listMembershipRequests(wanted);
      if (wanted === status.value) requests.value = rows; // a slower, outdated response must not win
    } catch {
      error.value = t("membership.admin.loadFailed");
    } finally {
      if (wanted === status.value) loading.value = false;
    }
  }

  watch(status, load, { immediate: true });

  /** A decided request leaves the list it was filtered into. */
  function drop(id: number) {
    requests.value = requests.value.filter((r) => r.id !== id);
  }

  async function approve(id: number, password: string): Promise<{ user?: CurrentUser; failure: string }> {
    try {
      return { user: await approveMembershipRequest(id, password), failure: "" };
    } catch (e) {
      return { failure: describeError(e, "membership.admin.actionFailed") };
    }
  }

  async function reject(id: number): Promise<string> {
    try {
      await rejectMembershipRequest(id);
      drop(id);
      return "";
    } catch (e) {
      return describeError(e, "membership.admin.actionFailed");
    }
  }

  return { status, requests, loading, error, approve, reject, drop };
}
