import { onMounted, ref } from "vue";
import { t } from "../i18n";
import { describeError } from "../i18n/apiErrors";
import { createUser, listUsers, updateUser } from "../api/users";
import type { CurrentUser, NewUser, UserUpdate } from "../api/types";

/** All users and the admin actions on them. Each action resolves to an error message, or "" on success. */
export function useAdminUsers() {
  const users = ref<CurrentUser[]>([]);
  const loading = ref(true);
  const error = ref("");

  onMounted(async () => {
    try {
      users.value = await listUsers();
    } catch {
      error.value = t("users.loadFailed");
    } finally {
      loading.value = false;
    }
  });

  async function add(user: NewUser): Promise<string> {
    try {
      const created = await createUser(user);
      users.value = [...users.value, created].sort((a, b) => a.username.localeCompare(b.username));
      return "";
    } catch (e) {
      return describeError(e, "users.createFailed");
    }
  }

  async function update(id: number, changes: UserUpdate): Promise<string> {
    try {
      const saved = await updateUser(id, changes);
      users.value = users.value.map((u) => (u.id === id ? saved : u));
      return "";
    } catch (e) {
      return describeError(e, "users.saveFailed");
    }
  }

  return { users, loading, error, add, update };
}
