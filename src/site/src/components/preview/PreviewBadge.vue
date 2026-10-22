<script setup lang="ts">
defineProps<{ tone?: "success" | "primary" | "warning" | "neutral" }>();
</script>

<template>
  <span class="badge" :class="tone ?? 'neutral'"><slot /></span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border: 1px solid transparent;
  border-radius: var(--radius-tag);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.success {
  background: var(--success-bg);
  color: var(--success-text);
  border-color: var(--success-border);
}
.warning {
  background: #fef3c7;
  color: #92400e;
}
.primary {
  background: var(--primary-tint);
  color: var(--primary);
}
.neutral {
  background: var(--surface-subdued);
  color: var(--text-secondary);
}
</style>
