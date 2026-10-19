import { ref } from "vue";
import { getCurrentUser } from "../api/auth";
import { getAuthHeader } from "../api/session";
import type { CurrentUser } from "../api/types";

const user = ref<CurrentUser | null>(null);
/** Credentials `user` was loaded for, so signing in as someone else refetches. */
let loadedFor: string | null = null;

/** The signed-in user (GET /auth/me), shared by all components. */
export function useCurrentUser() {
  async function load() {
    const header = getAuthHeader();
    if (user.value && loadedFor === header) return;
    user.value = null;
    loadedFor = header;
    user.value = await getCurrentUser();
  }

  return { user, load };
}
