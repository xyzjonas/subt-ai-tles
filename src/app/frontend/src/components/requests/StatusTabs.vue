<script setup lang="ts">
import type { RequestTab } from "../../composables/useRequests";

const model = defineModel<RequestTab>({ required: true });
defineProps<{ counts: Record<RequestTab, number> }>();

const TABS: { value: RequestTab; label: string }[] = [
  { value: "processing", label: "Processing" },
  { value: "completed", label: "Completed" },
];
</script>

<template>
  <div class="tabs" role="tablist">
    <button
      v-for="t in TABS"
      :key="t.value"
      type="button"
      role="tab"
      :aria-selected="model === t.value"
      :class="{ active: model === t.value }"
      @click="model = t.value"
    >
      {{ t.label }} ({{ counts[t.value] }})
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 4px;
  background: var(--surface-subdued);
  border-radius: var(--radius-md);
}

button {
  padding: 8px;
  border: 0;
  border-radius: var(--radius-sm);
  background: none;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
}

button.active {
  background: var(--surface);
  color: var(--primary);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1);
}
</style>
