<script setup lang="ts">
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ syncing: boolean }>();
defineEmits<{ download: []; sync: [] }>();
</script>

<template>
  <div class="bar">
    <div class="inner">
      <button type="button" class="primary" @click="$emit('download')">
        <AppIcon name="check" :size="18" /> {{ $t("editor.actionBar.download") }}
      </button>
      <button
        type="button"
        class="sync"
        :disabled="syncing"
        :aria-label="$t('editor.actionBar.sync')"
        @click="$emit('sync')"
      >
        <AppIcon name="sync" :size="16" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.bar {
  position: fixed;
  inset: auto 0 0;
  z-index: 10;
  height: var(--action-bar-height);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-top: 1px solid var(--border);
}

.inner {
  max-width: var(--content-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--page-padding);
  display: flex;
  align-items: center;
  gap: 12px;
}

.primary {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 48px;
  border: 0;
  border-radius: var(--radius-lg);
  background: var(--primary);
  box-shadow: var(--shadow-primary);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

.primary:hover {
  background: var(--primary-hover);
}

.sync {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-subdued);
  color: var(--text-secondary);
}

.sync:hover:not(:disabled) {
  background: var(--border);
}

.sync:disabled {
  opacity: 0.6;
  cursor: progress;
}
</style>
