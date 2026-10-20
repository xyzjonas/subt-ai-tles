<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import type { CurrentUser, UserUpdate } from "../../api/types";
import { generatePassword } from "../../utils/password";
import { formatWhen } from "../../utils/srt";
import UsageTab from "../dashboard/UsageTab.vue";
import AppIcon from "../ui/AppIcon.vue";
import TemporaryPasswordField from "./TemporaryPasswordField.vue";

const { t } = useI18n();
const props = defineProps<{
  user: CurrentUser;
  /** Whether this is the signed-in admin: they can't block themselves or reset their own password here. */
  self: boolean;
  update: (id: number, changes: UserUpdate) => Promise<string>;
}>();
defineEmits<{ back: [] }>();

const quota = ref(props.user.monthlyQuota);
const password = ref(generatePassword());
const saving = ref(false);
const error = ref("");
const notice = ref("");
/** The temporary password just set, shown once. */
const handedOver = ref("");

watch(
  () => props.user.monthlyQuota,
  (value) => (quota.value = value),
);

async function save(changes: UserUpdate, done: string) {
  saving.value = true;
  error.value = "";
  notice.value = "";
  error.value = await props.update(props.user.id, changes);
  if (!error.value) notice.value = done;
  saving.value = false;
  return !error.value;
}

const saveQuota = () => save({ monthlyQuota: quota.value }, t("users.manager.quotaSaved"));
const toggleBlocked = () =>
  save({ isActive: !props.user.isActive }, props.user.isActive ? t("users.manager.userBlocked") : t("users.manager.userUnblocked"));

async function resetPassword() {
  const set = password.value;
  if (await save({ password: set }, t("users.manager.passwordReset"))) {
    handedOver.value = set;
    password.value = generatePassword();
  }
}
</script>

<template>
  <div class="manager">
    <header class="head">
      <button type="button" class="back" :aria-label="t('users.manager.back')" @click="$emit('back')">
        <AppIcon name="back" :size="18" />
      </button>
      <div>
        <h2>{{ user.username }}</h2>
        <p>
          {{ user.isAdmin ? t("users.manager.administrator") : t("users.manager.member") }} · {{ t("users.manager.since") }}
          <time :datetime="user.createdAt">{{ formatWhen(user.createdAt) }}</time>
          <template v-if="!user.isActive"> · <strong class="blocked">{{ t("users.manager.blocked") }}</strong></template>
          <template v-else-if="user.mustChangePassword"> · {{ t("users.manager.temporaryPassword") }}</template>
        </p>
      </div>
    </header>

    <p v-if="notice" class="ok" role="status">{{ notice }}</p>
    <p v-if="error" class="fail" role="alert">{{ error }}</p>

    <form class="panel" @submit.prevent="saveQuota">
      <h3>{{ t("users.manager.quotaTitle") }}</h3>
      <label class="field">
        {{ t("users.manager.creditsPerMonth") }}
        <span class="row">
          <input v-model.number="quota" type="number" min="0" step="1" required />
          <button type="submit" class="primary" :disabled="saving || quota === user.monthlyQuota">{{ t("users.manager.save") }}</button>
        </span>
      </label>
    </form>

    <form v-if="!self" class="panel" @submit.prevent="resetPassword">
      <h3>{{ t("users.manager.resetTitle") }}</h3>
      <TemporaryPasswordField v-model="password" :label="t('users.manager.newTemporary')" />
      <button type="submit" class="secondary" :disabled="saving">{{ t("users.manager.reset") }}</button>
      <p v-if="handedOver" class="handover" role="status">
        <i18n-t keypath="users.manager.handover" scope="global">
          <template #username>{{ user.username }}</template>
          <template #password>
            <strong class="mono">{{ handedOver }}</strong>
          </template>
        </i18n-t>
      </p>
    </form>

    <section v-if="!self" class="panel" aria-labelledby="access-title">
      <h3 id="access-title">{{ t("users.manager.accessTitle") }}</h3>
      <p class="hint">
        {{ user.isActive ? t("users.manager.blockHint") : t("users.manager.blockedHint") }}
      </p>
      <button type="button" :class="user.isActive ? 'danger' : 'secondary'" :disabled="saving" @click="toggleBlocked">
        {{ user.isActive ? t("users.manager.block") : t("users.manager.unblock") }}
      </button>
    </section>

    <section class="usage" aria-labelledby="usage-title">
      <h3 id="usage-title">{{ t("users.manager.usage") }}</h3>
      <UsageTab :key="user.id + ':' + user.monthlyQuota" :user-id="user.id" />
    </section>
  </div>
</template>

<style scoped>
.manager {
  display: grid;
  gap: 16px;
}

.head {
  display: flex;
  align-items: center;
  gap: 12px;
}

.head h2 {
  font-size: 18px;
  font-weight: 700;
}

.head p {
  font-size: 13px;
  color: var(--text-secondary);
}

.back {
  display: grid;
  place-items: center;
  flex: none;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
}

.blocked {
  color: var(--danger);
}

.panel {
  display: grid;
  gap: 12px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

h3 {
  font-size: 16px;
  font-weight: 600;
}

.usage {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.row {
  display: flex;
  gap: 8px;
}

.row input {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

.row input:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

.hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.handover {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--success-bg);
  font-size: 13px;
  color: var(--success-text);
  overflow-wrap: anywhere;
}

.ok {
  font-size: 13px;
  font-weight: 600;
  color: var(--success-text);
}

.fail {
  font-size: 13px;
  color: var(--danger);
}

button:not(.back) {
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

.danger {
  border: 1px solid #fecaca;
  background: #fee2e2;
  color: #dc2626;
}
</style>
