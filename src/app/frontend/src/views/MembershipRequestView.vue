<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { submitMembershipRequest } from "../api/membershipRequests";
import { describeError } from "../i18n/apiErrors";
import AppIcon from "../components/ui/AppIcon.vue";
import LocaleSwitch from "../components/ui/LocaleSwitch.vue";

const { t } = useI18n();

/** The email becomes the username, which the backend caps at this length. */
const MAX_EMAIL_LENGTH = 64;

const email = ref("");
const details = ref("");
const submitting = ref(false);
const sent = ref(false);
const error = ref("");

async function submit() {
  submitting.value = true;
  error.value = "";
  try {
    await submitMembershipRequest(email.value.trim(), details.value);
    sent.value = true;
  } catch (e) {
    error.value = describeError(e, "membership.form.failed");
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <main class="page">
    <LocaleSwitch class="locale" />
    <section v-if="sent" class="card" aria-live="polite">
      <span class="emblem"><AppIcon name="translate" :size="22" /></span>
      <h1>{{ t("membership.sent.title") }}</h1>
      <p class="lead">{{ t("membership.sent.lead") }}</p>
      <RouterLink to="/login" class="back">{{ t("membership.form.backToLogin") }}</RouterLink>
    </section>

    <form v-else class="card" @submit.prevent="submit">
      <span class="emblem"><AppIcon name="translate" :size="22" /></span>
      <h1>{{ t("membership.form.title") }}</h1>
      <p class="lead">{{ t("membership.form.lead") }}</p>

      <label>
        {{ t("membership.form.email") }}
        <input
          v-model="email"
          type="email"
          name="email"
          autocomplete="email"
          autocapitalize="none"
          :maxlength="MAX_EMAIL_LENGTH"
          :title="t('membership.form.invalidEmail', { max: MAX_EMAIL_LENGTH })"
          required
          autofocus
        />
      </label>
      <label>
        {{ t("membership.form.details") }}
        <textarea v-model="details" name="details" rows="4" maxlength="1000" />
        <small>{{ t("membership.form.detailsHint") }}</small>
      </label>

      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <button type="submit" :disabled="submitting">{{ submitting ? t("membership.form.submitting") : t("membership.form.submit") }}</button>
      <RouterLink to="/login" class="back">{{ t("membership.form.backToLogin") }}</RouterLink>
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

input,
textarea {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

textarea {
  resize: vertical;
}

input:focus,
textarea:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

small {
  font-weight: 400;
  color: var(--text-muted);
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

.back {
  justify-self: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
}
</style>
