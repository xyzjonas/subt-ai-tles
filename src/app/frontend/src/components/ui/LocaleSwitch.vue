<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useLocalePreference } from "../../composables/useLocalePreference";
import { LOCALES, type Locale } from "../../i18n";

const { locale, t } = useI18n();
const { choose } = useLocalePreference();
</script>

<template>
  <div class="switch" role="group" :aria-label="t('locale.label')">
    <button
      v-for="code in LOCALES"
      :key="code"
      type="button"
      :aria-pressed="locale === code"
      :title="t(`locale.names.${code}`)"
      @click="choose(code as Locale)"
    >
      {{ code.toUpperCase() }}
    </button>
  </div>
</template>

<style scoped>
.switch {
  display: inline-flex;
  padding: 2px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
}

button {
  padding: 4px 8px;
  border: 0;
  border-radius: calc(var(--radius-sm) - 2px);
  background: none;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
}

button[aria-pressed="true"] {
  background: var(--surface);
  color: var(--primary);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(15, 23, 42, 0.08));
}
</style>
