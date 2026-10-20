<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { generatePassword, MIN_PASSWORD_LENGTH } from "../../utils/password";

const model = defineModel<string>({ required: true });
defineProps<{ label: string }>();

const { t } = useI18n();
</script>

<template>
  <label class="field">
    {{ label }}
    <span class="row">
      <input v-model="model" type="text" class="mono" autocomplete="off" autocapitalize="none" spellcheck="false" :minlength="MIN_PASSWORD_LENGTH" required />
      <button type="button" @click="model = generatePassword()">{{ t("users.password.generate") }}</button>
    </span>
    <small>{{ t("users.password.hint", { min: MIN_PASSWORD_LENGTH }) }}</small>
  </label>
</template>

<style scoped>
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

input {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font-size: 14px;
  color: var(--text);
}

input:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

button {
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
}

button:hover {
  background: var(--border);
}

small {
  font-weight: 400;
  color: var(--text-muted);
}
</style>
