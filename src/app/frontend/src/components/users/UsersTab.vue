<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useAdminUsers } from "../../composables/useAdminUsers";
import { useCurrentUser } from "../../composables/useCurrentUser";
import CreateUserForm from "./CreateUserForm.vue";
import UserList from "./UserList.vue";
import UserManager from "./UserManager.vue";

const { t } = useI18n();
const { users, loading, error, add, update } = useAdminUsers();
const { user: me, refresh } = useCurrentUser();

const selectedId = ref<number | null>(null);
const adding = ref(false);
const selected = computed(() => users.value.find((u) => u.id === selectedId.value));

/** Updating yourself (e.g. your own quota) also refreshes the account shown elsewhere. */
async function updateUser(...args: Parameters<typeof update>) {
  const failure = await update(...args);
  if (!failure && args[0] === me.value?.id) await refresh();
  return failure;
}
</script>

<template>
  <div class="users">
    <p v-if="loading" class="status" role="status">{{ t("loading") }}</p>
    <p v-else-if="error" class="status" role="alert">{{ error }}</p>

    <UserManager v-else-if="selected" :user="selected" :self="selected.id === me?.id" :update="updateUser" @back="selectedId = null" />

    <template v-else>
      <CreateUserForm v-if="adding" :add="add" @close="adding = false" />
      <template v-else>
        <header class="bar">
          <p>{{ t("users.count", { count: users.length }, users.length) }}</p>
          <button type="button" @click="adding = true">{{ t("users.add") }}</button>
        </header>
        <UserList :users="users" :current-id="me?.id" @select="selectedId = $event" />
      </template>
    </template>
  </div>
</template>

<style scoped>
.users {
  display: grid;
  gap: 16px;
}

.status {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}

.bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bar p {
  font-size: 13px;
  color: var(--text-secondary);
}

button {
  height: 40px;
  padding: 0 18px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  box-shadow: var(--shadow-primary);
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

button:hover {
  background: var(--primary-hover);
}
</style>
