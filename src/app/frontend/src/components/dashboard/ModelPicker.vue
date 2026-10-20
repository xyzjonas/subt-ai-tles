<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { ModelOption } from "../../api/types";
import { formatCredits } from "../../utils/usage";

const model = defineModel<string>({ required: true });
defineProps<{ models: ModelOption[] }>();

const { t, te } = useI18n();

/** Localized description by model id; models added later fall back to the backend's text. */
function description(m: ModelOption): string {
  const key = `dashboard.models.${m.id.replace(/[.-]/g, "_")}`;
  return te(key) ? t(key) : m.description;
}
</script>

<template>
  <fieldset class="picker">
    <legend>{{ t("dashboard.models.legend") }}</legend>
    <p class="hint">{{ t("dashboard.models.hint") }}</p>
    <div class="cards">
      <label v-for="m in models" :key="m.id" class="card">
        <input v-model="model" type="radio" name="model" :value="m.id" />
        <span class="body">
          <strong>{{ m.label }}</strong>
          <span class="description">{{ description(m) }}</span>
          <span class="rates mono">
            {{ t("dashboard.models.rates", { input: formatCredits(m.inputCreditsPer1K), output: formatCredits(m.outputCreditsPer1K) }) }}
            <small>{{ t("dashboard.models.ratesUnit") }}</small>
          </span>
        </span>
      </label>
    </div>
  </fieldset>
</template>

<style scoped>
.picker {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}

legend {
  padding: 0;
  margin-bottom: 4px;
  font-size: 16px;
  font-weight: 600;
}

.hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.cards {
  display: grid;
  gap: 10px;
}

.card {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
}

.card:hover {
  border-color: var(--primary);
}

.card:has(input:checked) {
  border-color: var(--primary);
  background: var(--primary-tint);
  box-shadow: 0 0 0 1px var(--primary);
}

.card:has(input:focus-visible) {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

input {
  margin: 3px 0 0;
  accent-color: var(--primary);
}

.body {
  display: grid;
  gap: 4px;
}

strong {
  font-size: 14px;
}

.description {
  font-size: 13px;
  color: var(--text-secondary);
}

.rates {
  font-size: 12px;
  color: var(--text-muted);
}

.rates small {
  font-family: var(--font-sans);
  font-size: 11px;
}
</style>
