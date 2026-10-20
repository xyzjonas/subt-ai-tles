<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { login } from "../api/auth";
import { describeError } from "../i18n/apiErrors";
import AppIcon from "../components/ui/AppIcon.vue";
import LocaleSwitch from "../components/ui/LocaleSwitch.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const username = ref("");
const password = ref("");
const submitting = ref(false);
const error = ref("");

/** Only same-origin paths: `//host` and absolute URLs would make this an open redirect. */
const destination = computed(() => {
  const target = route.query.redirect;
  return typeof target === "string" && target.startsWith("/") && !target.startsWith("//") ? target : "/";
});

async function submit() {
  submitting.value = true;
  error.value = "";
  try {
    await login(username.value, password.value);
    await router.replace(destination.value);
  } catch (e) {
    error.value = describeError(e, "auth.login.failed");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="page">
    <LocaleSwitch class="locale" />
    <form class="card" @submit.prevent="submit">
      <span class="emblem"><AppIcon name="translate" :size="22" /></span>
      <h1>{{ t("auth.login.title") }}</h1>
      <p class="lead">{{ t("auth.login.lead") }}</p>

      <label>
        {{ t("auth.login.username") }}
        <input v-model="username" type="text" name="username" autocomplete="username" autocapitalize="none" required autofocus />
      </label>
      <label>
        {{ t("auth.login.password") }}
        <input v-model="password" type="password" name="password" autocomplete="current-password" required />
      </label>

      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <button type="submit" :disabled="submitting">{{ submitting ? t("auth.login.submitting") : t("auth.login.submit") }}</button>
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

button {
  height: 48px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  box-shadow: 0 4px 14px var(--primary-glow);
  color: #fff;
  font-weight: 600;
}

button:hover:not(:disabled) {
  background: var(--primary-hover);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
