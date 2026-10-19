<script setup lang="ts">
defineProps<{ tone?: "success" | "primary" | "neutral"; dot?: boolean; pulse?: boolean }>();
</script>

<template>
  <span class="badge" :class="tone ?? 'neutral'">
    <span v-if="dot" class="dot" :class="{ pulse }" />
    <slot />
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.success {
  background: var(--success-bg);
  color: var(--success-text);
  border-color: var(--success-border);
}

.primary {
  background: var(--primary-tint);
  color: var(--primary);
}

.neutral {
  background: var(--surface-subdued);
  color: var(--text-secondary);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
}

.pulse {
  animation: pulse 1.8s ease-in-out infinite;
}

@keyframes pulse {
  50% {
    opacity: 0.35;
    transform: scale(0.8);
  }
}
</style>
