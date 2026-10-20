import { ref } from "vue";
import { getCurrentUser } from "../api/auth";
import { getAuthHeader } from "../api/session";
import type { CurrentUser } from "../api/types";
import { setLocale } from "../i18n";

const user = ref<CurrentUser | null>(null);
/** Credentials `user` was loaded for, so signing in as someone else refetches. */
let loadedFor: string | null = null;

/** A language saved on the account wins over (and replaces) the one stored in the browser. */
function applyLocale() {
  if (user.value?.locale) setLocale(user.value.locale);
}

/** The signed-in user (GET /auth/me), shared by all components. */
export function useCurrentUser() {
  async function load() {
    const header = getAuthHeader();
    if (user.value && loadedFor === header) return;
    user.value = null;
    loadedFor = header;
    user.value = await getCurrentUser();
    applyLocale();
  }

  /** Refetches after the account changed, e.g. a new password. */
  async function refresh() {
    loadedFor = getAuthHeader();
    user.value = await getCurrentUser();
    applyLocale();
  }

  return { user, load, refresh };
}
