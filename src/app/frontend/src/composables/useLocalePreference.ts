import { ref } from "vue";
import { updateProfile } from "../api/auth";
import { type Locale, resetLocale, setLocale } from "../i18n";
import { describeError } from "../i18n/apiErrors";
import { useCurrentUser } from "./useCurrentUser";

/**
 * Changes the UI language right away and, when signed in, saves it on the account.
 * `null` means "automatic": the account stores nothing and the browser's language is used.
 */
export function useLocalePreference() {
  const { user } = useCurrentUser();
  const saving = ref(false);
  const error = ref("");

  async function choose(locale: Locale | null) {
    error.value = "";
    if (locale) setLocale(locale);
    else resetLocale();
    if (!user.value) return;
    saving.value = true;
    try {
      user.value = await updateProfile(locale);
    } catch (e) {
      error.value = describeError(e, "errors.unknown");
    } finally {
      saving.value = false;
    }
  }

  return { user, saving, error, choose };
}
