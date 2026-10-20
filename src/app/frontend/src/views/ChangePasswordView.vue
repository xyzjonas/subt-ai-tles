<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { changePassword } from "../api/auth";
import { clearSession } from "../api/session";
import { describeError } from "../i18n/apiErrors";
import AppIcon from "../components/ui/AppIcon.vue";
import LocaleSwitch from "../components/ui/LocaleSwitch.vue";
import { useCurrentUser } from "../composables/useCurrentUser";

const MIN_LENGTH = 8;

const { t } = useI18n();
const router = useRouter();
const { user, load, refresh } = useCurrentUser();
onMounted(load);

const current = ref("");
const next = ref("");
const confirm = ref("");
const submitting = ref(false);
const error = ref("");

const mismatch = computed(() => confirm.value !== "" && confirm.value !== next.value);

async function submit() {
  if (!user.value || mismatch.value) return;
  submitting.value = true;
  error.value = "";
  try {
    await changePassword(user.value.username, current.value, next.value);
    await refresh();
    await router.replace("/");
  } catch (e) {
    error.value = describeError(e, "auth.changePassword.failed");
  } finally {
    submitting.value = false;
  }
}

function signOut() {
  clearSession();
  router.push({ name: "login" });
}
</script>

<template>
  <main class="page">
    <LocaleSwitch class="locale" />
    <form class="card" @submit.prevent="submit">
      <span class="emblem"><AppIcon name="user" :size="22" /></span>
      <h1>{{ t("auth.changePassword.title") }}</h1>
      <p class="lead">{{ t("auth.changePassword.lead") }}</p>

      <label>
        {{ t("auth.changePassword.temporary") }}
        <input v-model="current" type="password" name="current-password" autocomplete="current-password" required autofocus />
      </label>
      <label>
        {{ t("auth.changePassword.next") }}
        <input v-model="next" type="password" name="new-password" autocomplete="new-password" :minlength="MIN_LENGTH" required />
        <small>{{ t("auth.changePassword.hint", { min: MIN_LENGTH }) }}</small>
      </label>
      <label>
        {{ t("auth.changePassword.repeat") }}
        <input v-model="confirm" type="password" name="confirm-password" autocomplete="new-password" required />
      </label>

      <p v-if="mismatch" class="error" role="alert">{{ t("auth.changePassword.mismatch") }}</p>
      <p v-else-if="error" class="error" role="alert">{{ error }}</p>

      <button type="submit" class="primary" :disabled="submitting || mismatch || !user">
        {{ submitting ? t("auth.changePassword.submitting") : t("auth.changePassword.submit") }}
      </button>
      <button type="button" class="link" @click="signOut">{{ t("auth.changePassword.signOut") }}</button>
    </form>
  </main>
</template>

<style scoped>
.locale {
  position: fixed;
  top: 16px;
  right: var(--page-padding);
}

.page {
  display: grid;
  place-items: center;
  min-height: 100dvh;
  padding: var(--page-padding);
}

.card {
  display: grid;
  gap: 14px;
  width: min(100%, 380px);
  padding: 28px 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.emblem {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
}

h1 {
  margin: 0;
  font-size: 24px;
  line-height: 1.25;
  letter-spacing: -0.02em;
}

.lead {
  margin: -8px 0 6px;
  color: var(--text-secondary);
}

label {
  display: grid;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

label small {
  font-weight: 400;
  color: var(--text-muted);
}

input {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

input:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

.error {
  font-size: 13px;
  color: var(--danger);
}

.primary {
  height: 48px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  box-shadow: 0 4px 14px var(--primary-glow);
  color: #fff;
  font-weight: 600;
}

.primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.link {
  border: 0;
  background: none;
  font: inherit;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}
</style>
