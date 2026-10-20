<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { Job } from "../../api/types";
import { languageCode } from "../../utils/language";
import { timeAgo } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ job: Job }>();

const { t } = useI18n();
</script>

<template>
  <RouterLink :to="{ name: job.status === 'ready' ? 'editor' : 'job', params: { id: job.id } }" class="item">
    <span class="icon"><AppIcon name="file" :size="18" /></span>
    <span class="info">
      <span class="name mono">{{ job.fileName }}</span>
      <span class="meta">
        <span class="langs">
          {{ languageCode(job.sourceLang) }} <AppIcon name="arrow" :size="12" /> {{ job.targetLang.toUpperCase() }}
        </span>
        • {{ t("cues", { count: job.cueCount }, job.cueCount) }} • {{ timeAgo(job.createdAt) }}
      </span>
    </span>
    <StatusBadge :tone="job.status === 'ready' ? 'success' : 'neutral'">
      {{ t(`status.${job.status}`) }}
    </StatusBadge>
  </RouterLink>
</template>

<style scoped>
.item {
  display: flex;
  align-items: center;
  align-self: stretch;
  height: 100%;
  box-sizing: border-box;
  gap: 12px;
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
}

.item:hover {
  border-color: var(--primary);
}

.icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  color: var(--text-secondary);
}

.info {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 2px;
}

.name {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  font-size: 11px;
  color: var(--text-muted);
}

.langs {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  vertical-align: middle;
}
</style>
