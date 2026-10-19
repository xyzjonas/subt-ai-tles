<script setup lang="ts">
defineProps<{ active: boolean }>();
</script>

<template>
  <button type="button" class="pill" :class="{ active }" :aria-pressed="active">
    <slot />
  </button>
</template>

<style scoped>
.pill {
  height: 36px;
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

.pill:hover {
  background: var(--border);
}

.pill.active {
  background: var(--primary-tint);
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 600;
}
</style>
