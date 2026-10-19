<script setup lang="ts" generic="T extends string">
const model = defineModel<T>({ required: true });
defineProps<{ tabs: { value: T; label: string }[]; label?: string }>();
</script>

<template>
  <div class="tabs" role="tablist" :aria-label="label" :style="{ '--count': tabs.length }">
    <button
      v-for="t in tabs"
      :key="t.value"
      type="button"
      role="tab"
      :aria-selected="model === t.value"
      :class="{ active: model === t.value }"
      @click="model = t.value"
    >
      {{ t.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: grid;
  grid-template-columns: repeat(var(--count), 1fr);
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
