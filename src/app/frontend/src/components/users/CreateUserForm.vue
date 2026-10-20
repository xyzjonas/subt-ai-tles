<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { NewUser } from "../../api/types";
import { LOCALES, type Locale } from "../../i18n";
import { generatePassword } from "../../utils/password";
import TemporaryPasswordField from "./TemporaryPasswordField.vue";

const { t } = useI18n();
const props = defineProps<{ add: (user: NewUser) => Promise<string> }>();
const emit = defineEmits<{ close: [] }>();

const username = ref("");
const password = ref(generatePassword());
const isAdmin = ref(false);
/** Empty leaves it unset, so the user's browser decides. */
const locale = ref<Locale | "">("");
/** Empty keeps the server default. */
const quota = ref<number | "">("");
const saving = ref(false);
const error = ref("");
/** Credentials of the user just created, shown once so the admin can hand them over. */
const created = ref<{ username: string; password: string } | null>(null);

async function submit() {
  saving.value = true;
  error.value = "";
  const user = { username: username.value.trim(), password: password.value, isAdmin: isAdmin.value, monthlyQuota: quota.value === "" ? undefined : quota.value, locale: locale.value || null };
  error.value = await props.add(user);
  if (!error.value) created.value = { username: user.username, password: user.password };
  saving.value = false;
}
</script>

<template>
  <section class="create" aria-labelledby="create-title">
    <template v-if="created">
      <h2 id="create-title">{{ t("users.create.created") }}</h2>
      <p class="ok" role="status">
        <i18n-t keypath="users.create.share" scope="global">
          <template #username>
            <strong>{{ created.username }}</strong>
          </template>
        </i18n-t>
      </p>
      <dl class="credentials">
        <div>
          <dt>{{ t("users.create.username") }}</dt>
          <dd class="mono">{{ created.username }}</dd>
        </div>
        <div>
          <dt>{{ t("users.create.temporary") }}</dt>
          <dd class="mono">{{ created.password }}</dd>
        </div>
      </dl>
      <button type="button" class="primary" @click="emit('close')">{{ t("users.create.done") }}</button>
    </template>

    <form v-else @submit.prevent="submit">
      <h2 id="create-title">{{ t("users.create.title") }}</h2>
      <label class="field">
        {{ t("users.create.username") }}
        <input v-model="username" type="text" maxlength="64" pattern="\S+" :title="t('users.create.noSpaces')" autocomplete="off" autocapitalize="none" required autofocus />
      </label>
      <TemporaryPasswordField v-model="password" :label="t('users.create.temporary')" />
      <label class="field">
        {{ t("users.create.quota") }}
        <input v-model.number="quota" type="number" min="0" step="1" :placeholder="t('users.create.quotaDefault')" />
      </label>
      <label class="field">
        {{ t("locale.setting") }}
        <select v-model="locale">
          <option value="">{{ t("locale.auto") }}</option>
          <option v-for="code in LOCALES" :key="code" :value="code">{{ t(`locale.names.${code}`) }}</option>
        </select>
      </label>
      <label class="check">
        <input v-model="isAdmin" type="checkbox" />
        {{ t("users.create.administrator") }}
      </label>
      <p v-if="error" class="fail" role="alert">{{ error }}</p>
      <div class="actions">
        <button type="button" class="secondary" @click="emit('close')">{{ t("users.create.cancel") }}</button>
        <button type="submit" class="primary" :disabled="saving">{{ saving ? t("users.create.submitting") : t("users.create.submit") }}</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.create,
form {
  display: grid;
  gap: 14px;
}

.create {
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

h2 {
  font-size: 16px;
  font-weight: 600;
}

.field {
  display: grid;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.field input,
.field select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

.field input:focus,
.field select:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

.check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.credentials {
  display: grid;
  margin: 0;
  background: var(--surface-subdued);
  border-radius: var(--radius-md);
}

.credentials div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
}

dt {
  color: var(--text-secondary);
}

dd {
  margin: 0;
  font-weight: 600;
  overflow-wrap: anywhere;
}

.ok {
  font-size: 13px;
  color: var(--success-text);
}

.fail {
  font-size: 13px;
  color: var(--danger);
}

.actions {
  display: flex;
  gap: 10px;
}

button {
  height: 44px;
  padding: 0 20px;
  border-radius: var(--radius-lg);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary {
  flex: 1;
  border: 0;
  background: var(--primary);
  color: #fff;
  box-shadow: var(--shadow-primary);
}

.primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.secondary {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
}
</style>
