<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{ percent: number; processed: number; total: number; chunkPercent: number }>();

const { t } = useI18n();

const RADIUS = 80;
const circumference = 2 * Math.PI * RADIUS;
const offset = computed(() => circumference * (1 - props.percent / 100));
</script>

<template>
  <section class="gauge" :aria-label="t('progress.gauge.label')">
    <div class="ring">
      <svg viewBox="0 0 180 180" aria-hidden="true">
        <circle class="track" cx="90" cy="90" :r="RADIUS" />
        <circle class="fill" cx="90" cy="90" :r="RADIUS" :stroke-dasharray="circumference" :stroke-dashoffset="offset" />
      </svg>
      <p class="label">
        <output class="percent">{{ percent }}%</output>
        <span class="lines">{{ t("progress.gauge.lines", { processed, total }) }}</span>
      </p>
    </div>

    <p class="tagline"><span class="dot" /> {{ t("progress.gauge.tagline") }}</p>
    <p class="note">{{ t("progress.gauge.note") }}</p>
    <progress class="chunk" :value="chunkPercent" max="100" :aria-label="t('progress.gauge.chunk')" />
  </section>
</template>

<style scoped>
.gauge {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 24px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.ring {
  position: relative;
  width: 170px;
  height: 170px;
}

svg {
  width: 100%;
  height: 100%;
  rotate: -90deg;
}

circle {
  fill: none;
  stroke-width: 12;
}

.track {
  stroke: #e0e7ff;
}

.fill {
  stroke: var(--primary);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}

.label {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  gap: 2px;
}

.percent {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

.lines {
  font-size: 13px;
  color: var(--text-muted);
}

.tagline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  animation: pulse 1.8s ease-in-out infinite;
}

.note {
  font-size: 13px;
  color: var(--text-secondary);
}

.chunk {
  width: 100%;
  height: 4px;
  margin-top: 8px;
  border: 0;
  border-radius: 4px;
  appearance: none;
}

.chunk::-webkit-progress-bar {
  background: var(--surface-subdued);
  border-radius: 4px;
}

.chunk::-webkit-progress-value {
  background: var(--primary);
  border-radius: 4px;
  transition: width 0.4s ease;
}

.chunk::-moz-progress-bar {
  background: var(--primary);
  border-radius: 4px;
}

@keyframes pulse {
  50% {
    opacity: 0.35;
    transform: scale(0.8);
  }
}

@media (prefers-reduced-motion: reduce) {
  .fill,
  .dot {
    transition: none;
    animation: none;
  }
}
</style>
