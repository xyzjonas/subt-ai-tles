<script setup lang="ts">
import { formatSize } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ file: File; cueCount: number }>();
defineEmits<{ remove: [] }>();
</script>

<template>
  <div class="card">
    <span class="icon"><AppIcon name="file" /></span>
    <div class="info">
      <p class="name mono">{{ file.name }}</p>
      <p class="meta">{{ formatSize(file.size) }} • {{ cueCount.toLocaleString() }} dialogue cues</p>
      <div class="tags">
        <StatusBadge tone="success" dot>Validated UTF-8</StatusBadge>
        <StatusBadge>Encoding: OK</StatusBadge>
      </div>
    </div>
    <button type="button" class="remove" aria-label="Remove file" @click="$emit('remove')">
      <AppIcon name="close" :size="16" />
    </button>
  </div>
</template>

<style scoped>
.card {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  background: var(--primary-tint);
  color: var(--primary);
}

.info {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 4px;
}

.name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  font-size: 12px;
  color: var(--text-muted);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.remove {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--text-muted);
}

.remove:hover {
  background: var(--border);
}
</style>
