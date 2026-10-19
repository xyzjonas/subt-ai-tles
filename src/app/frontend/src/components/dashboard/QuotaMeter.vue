<script setup lang="ts">
import { computed } from "vue";
import type { Quota } from "../../api/types";
import { formatCredits } from "../../utils/usage";

const props = defineProps<{ quota: Quota }>();

const WARN_AT = 0.8;

const ratio = computed(() => (props.quota.limit > 0 ? Math.min(1, props.quota.used / props.quota.limit) : 1));
const tone = computed(() => (ratio.value >= 1 ? "danger" : ratio.value >= WARN_AT ? "warning" : "ok"));
</script>

<template>
  <section class="quota" aria-labelledby="quota-title">
    <header>
      <h2 id="quota-title">Monthly quota</h2>
      <span class="percent mono" :data-tone="tone">{{ Math.round(ratio * 100) }}%</span>
    </header>
    <progress :value="quota.used" :max="quota.limit || 1" :data-tone="tone" aria-labelledby="quota-title" />
    <p class="figures">
      <span class="mono">{{ formatCredits(quota.used) }}</span> of
      <span class="mono">{{ formatCredits(quota.limit) }}</span> credits used ·
      <span class="mono">{{ formatCredits(quota.remaining) }}</span> left
    </p>
    <p v-if="tone === 'danger'" class="notice" role="alert">
      You have used your quota. New translations are paused until it resets next month.
    </p>
  </section>
</template>

<style scoped>
.quota {
  display: grid;
  gap: 10px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

h2 {
  font-size: 16px;
  font-weight: 600;
}

.percent {
  font-size: 13px;
  color: var(--primary);
}

.percent[data-tone="warning"] {
  color: var(--warning-strong);
}

.percent[data-tone="danger"] {
  color: var(--danger);
}

progress {
  appearance: none;
  width: 100%;
  height: 10px;
  border: 0;
  border-radius: 999px;
  overflow: hidden;
  background: var(--surface-subdued);
  --fill: var(--primary);
}

progress[data-tone="warning"] {
  --fill: var(--warning);
}

progress[data-tone="danger"] {
  --fill: var(--danger);
}

progress::-webkit-progress-bar {
  background: var(--surface-subdued);
}

progress::-webkit-progress-value {
  background: var(--fill);
  border-radius: 999px;
}

progress::-moz-progress-bar {
  background: var(--fill);
  border-radius: 999px;
}

.figures {
  font-size: 13px;
  color: var(--text-secondary);
}

.notice {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: var(--danger-bg);
  font-size: 13px;
  color: var(--danger);
}
</style>
