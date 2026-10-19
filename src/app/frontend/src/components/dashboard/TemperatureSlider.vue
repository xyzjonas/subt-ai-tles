<script setup lang="ts">
import { computed } from "vue";

const temperature = defineModel<number>({ required: true });
const props = defineProps<{ supported: boolean; modelLabel: string }>();

const percent = computed(() => `${temperature.value * 100}%`);
const wording = computed(() => {
  if (temperature.value <= 0.2) return "Very consistent: the same input gives the same translation.";
  if (temperature.value <= 0.6) return "Balanced: mostly consistent, with some variety in wording.";
  return "Creative: freer, more varied wording. Less predictable.";
});
</script>

<template>
  <section class="temperature" aria-labelledby="temperature-label">
    <header>
      <label id="temperature-label" for="temperature">Creativity (temperature)</label>
      <output for="temperature" class="value mono">{{ temperature.toFixed(1) }}</output>
    </header>
    <p id="temperature-help" class="hint">
      How freely the model words its translations. Lower values give steadier, more predictable subtitles, which is
      usually best. Higher values allow looser, more creative phrasing.
    </p>

    <input
      id="temperature"
      v-model.number="temperature"
      type="range"
      min="0"
      max="1"
      step="0.1"
      :disabled="!supported"
      aria-describedby="temperature-help temperature-current"
      :style="{ '--fill': percent }"
    />
    <div class="ends" aria-hidden="true">
      <span>Literal · consistent</span>
      <span>Creative · varied</span>
    </div>

    <p v-if="supported" id="temperature-current" class="current">{{ wording }}</p>
    <p v-else id="temperature-current" class="current unsupported">
      {{ props.modelLabel }} manages its own randomness, so this setting is ignored for it. Your value is kept for models
      that use it.
    </p>
  </section>
</template>

<style scoped>
.temperature {
  display: grid;
  gap: 10px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

label {
  font-size: 16px;
  font-weight: 600;
}

.value {
  padding: 2px 10px;
  border-radius: var(--radius-tag);
  background: var(--primary-tint);
  color: var(--primary);
  font-size: 13px;
}

.hint,
.current {
  font-size: 13px;
  color: var(--text-secondary);
}

.unsupported {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: var(--warning-bg);
  color: var(--warning-strong);
}

input[type="range"] {
  appearance: none;
  width: 100%;
  height: 8px;
  margin: 8px 0 0;
  border-radius: 999px;
  background: linear-gradient(to right, var(--primary) var(--fill), var(--border) var(--fill));
  cursor: pointer;
}

input[type="range"]:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 22px;
  height: 22px;
  border: 3px solid var(--surface);
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.35);
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border: 3px solid var(--surface);
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.35);
}

input[type="range"]:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 6px;
}

.ends {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
}
</style>
