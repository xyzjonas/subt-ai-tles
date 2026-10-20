<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useLocalePreference } from "../../composables/useLocalePreference";
import { LOCALES, type Locale } from "../../i18n";

const { t } = useI18n();
const { user, saving, error, choose } = useLocalePreference();

function onChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value;
  choose(value === "" ? null : (value as Locale));
}
</script>

<template>
  <div class="setting">
    <select id="ui-language" :value="user?.locale ?? ''" :disabled="saving || !user" @change="onChange">
      <option value="">{{ t("locale.auto") }}</option>
      <option v-for="code in LOCALES" :key="code" :value="code">{{ t(`locale.names.${code}`) }}</option>
    </select>
    <small v-if="error" class="fail" role="alert">{{ error }}</small>
  </div>
</template>

<style scoped>
.setting {
  display: grid;
  justify-items: end;
  gap: 4px;
}

select {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

.fail {
  color: var(--danger);
}
</style>
