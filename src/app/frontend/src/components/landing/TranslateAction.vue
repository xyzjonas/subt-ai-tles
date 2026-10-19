<script setup lang="ts">
import type { JobEstimate } from "../../api/types";
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ estimate: JobEstimate | null; disabled: boolean; submitting: boolean; error: string }>();
defineEmits<{ submit: [] }>();
</script>

<template>
  <section class="action">
    <button type="button" class="cta" :disabled="disabled" @click="$emit('submit')">
      {{ submitting ? "Starting…" : "⚡ Translate Subtitles (LLM) →" }}
    </button>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <div class="estimate mono">
      <span><AppIcon name="clock" :size="14" /> Est. processing: {{ estimate ? `~${estimate.seconds}s` : "—" }}</span>
      <span><AppIcon name="gear" :size="14" /> {{ estimate ? `~${estimate.tokens.toLocaleString()} tokens` : "—" }}</span>
    </div>
  </section>
</template>

<style scoped>
.action {
  display: grid;
  gap: 10px;
}

.cta {
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

.error {
  font-size: 13px;
  color: #b91c1c;
  text-align: center;
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
