<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useAdminSettings } from "../../composables/useAdminSettings";
import ModelPicker from "./ModelPicker.vue";
import TemperatureSlider from "./TemperatureSlider.vue";

const { t } = useI18n();
const { saved, draft, selected, dirty, loading, saving, justSaved, error, save, reset } = useAdminSettings();
</script>

<template>
  <div class="settings">
    <p v-if="loading" class="status" role="status">{{ t("loading") }}</p>
    <p v-else-if="!saved" class="status" role="alert">{{ error }}</p>
    <form v-else @submit.prevent="save">
      <p class="intro">{{ t("dashboard.settings.intro") }}</p>

      <ModelPicker v-model="draft.model" :models="saved.models" />
      <TemperatureSlider
        v-model="draft.temperature"
        :supported="selected?.supportsTemperature ?? true"
        :model-label="selected?.label ?? t('dashboard.models.thisModel')"
      />

      <footer class="bar">
        <p class="note">{{ t("dashboard.settings.note") }}</p>
        <div class="actions">
          <button type="button" class="secondary" :disabled="!dirty || saving" @click="reset">{{ t("dashboard.settings.reset") }}</button>
          <button type="submit" class="primary" :disabled="!dirty || saving">
            {{ saving ? t("dashboard.settings.saving") : t("dashboard.settings.save") }}
          </button>
        </div>
        <p v-if="justSaved && !dirty" class="ok" role="status">{{ t("dashboard.settings.saved") }}</p>
        <p v-if="error" class="fail" role="alert">{{ error }}</p>
      </footer>
    </form>
  </div>
</template>

<style scoped>
form {
  display: grid;
  gap: 28px;
}

.intro {
  font-size: 13px;
  color: var(--text-secondary);
}

.status {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}

.bar {
  display: grid;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.note {
  font-size: 12px;
  color: var(--text-muted);
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

.ok {
  font-size: 13px;
  font-weight: 600;
  color: var(--success-text);
}

.fail {
  font-size: 13px;
  color: var(--danger);
}
</style>
