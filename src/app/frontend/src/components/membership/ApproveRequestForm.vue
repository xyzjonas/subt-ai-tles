<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { CurrentUser } from "../../api/types";
import { generatePassword } from "../../utils/password";
import TemporaryPasswordField from "../users/TemporaryPasswordField.vue";

const { t } = useI18n();
const props = defineProps<{ email: string; approve: (password: string) => Promise<{ user?: CurrentUser; failure: string }> }>();
const emit = defineEmits<{ cancel: []; done: [] }>();

const password = ref(generatePassword());
const saving = ref(false);
const error = ref("");
/** Credentials of the user just created, shown once so the admin can hand them over. */
const created = ref<{ username: string; password: string } | null>(null);

async function submit() {
  saving.value = true;
  error.value = "";
  const { user, failure } = await props.approve(password.value);
  if (user) created.value = { username: user.username, password: password.value };
  error.value = failure;
  saving.value = false;
}
</script>

<template>
  <section v-if="created" class="approve" aria-live="polite">
    <h3>{{ t("membership.admin.approved") }}</h3>
    <p class="ok">
      <i18n-t keypath="membership.admin.share" scope="global">
        <template #username>
          <strong>{{ created.username }}</strong>
        </template>
      </i18n-t>
    </p>
    <dl class="credentials">
      <div>
        <dt>{{ t("membership.admin.username") }}</dt>
        <dd class="mono">{{ created.username }}</dd>
      </div>
      <div>
        <dt>{{ t("membership.admin.temporary") }}</dt>
        <dd class="mono">{{ created.password }}</dd>
      </div>
    </dl>
    <button type="button" class="primary" @click="emit('done')">{{ t("membership.admin.done") }}</button>
  </section>

  <form v-else class="approve" @submit.prevent="submit">
    <h3>{{ t("membership.admin.approveTitle", { email }) }}</h3>
    <TemporaryPasswordField v-model="password" :label="t('membership.admin.temporary')" />
    <p v-if="error" class="fail" role="alert">{{ error }}</p>
    <div class="actions">
      <button type="button" class="secondary" :disabled="saving" @click="emit('cancel')">{{ t("membership.admin.cancel") }}</button>
      <button type="submit" class="primary" :disabled="saving">{{ saving ? t("membership.admin.confirming") : t("membership.admin.confirm") }}</button>
    </div>
  </form>
</template>

<style scoped>
.approve {
  display: grid;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

h3 {
  font-size: 14px;
  font-weight: 600;
  overflow-wrap: anywhere;
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
