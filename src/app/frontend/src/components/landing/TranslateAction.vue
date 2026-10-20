<script setup lang="ts">
import type { JobEstimate } from "../../api/types";
import { useI18n } from "vue-i18n";
import AppIcon from "../ui/AppIcon.vue";
import ErrorBanner from "../ui/ErrorBanner.vue";

defineProps<{ estimate: JobEstimate | null; disabled: boolean; submitting: boolean; error: string }>();
defineEmits<{ submit: [] }>();

const { t, n } = useI18n();
</script>

<template>
  <section class="action">
    <button type="button" class="cta" :disabled="disabled" @click="$emit('submit')">
      <AppIcon name="bolt" :size="18" />
      {{ submitting ? t("translate.action.starting") : t("translate.action.start") }}
      <AppIcon v-if="!submitting" name="arrow" :size="18" />
    </button>
    <ErrorBanner v-if="error" :title="t('translate.action.startFailed')" :message="error" />
    <div class="estimate mono">
      <span><AppIcon name="clock" :size="14" /> {{ t("translate.action.estimate", { value: estimate ? t("translate.action.seconds", { n: estimate.seconds }) : "—" }) }}</span>
      <span><AppIcon name="gear" :size="14" /> {{ estimate ? t("translate.action.tokens", { n: n(estimate.tokens) }) : "—" }}</span>
    </div>
  </section>
</template>

<style scoped>
.action {
  display: grid;
  gap: 10px;
}

.cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 52px;
  border: 0;
  border-radius: var(--radius-lg);
  background: var(--primary);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  box-shadow: var(--shadow-primary);
}

.cta:hover:not(:disabled) {
  background: var(--primary-hover);
}

.cta:disabled {
  background: #c7d2fe;
  box-shadow: none;
  cursor: not-allowed;
}

.estimate {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}

.estimate span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
</style>
