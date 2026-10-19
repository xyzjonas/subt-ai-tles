<script setup lang="ts">
import type { Job } from "../../api/types";
import { timeAgo } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ job: Job }>();

const lang = (code: string) => new Intl.DisplayNames("en", { type: "language" }).of(code) ?? code;
</script>

<template>
  <section class="card" aria-label="Job overview">
    <header class="head">
      <span class="icon"><AppIcon name="file" :size="18" /></span>
      <h2 class="name mono">{{ job.fileName }}</h2>
      <StatusBadge tone="success" dot pulse>Live</StatusBadge>
    </header>
    <p class="specs mono">SubRip (.srt) • UTF-8 • Submitted {{ timeAgo(job.createdAt) }}</p>

    <p class="route">
      <span class="lang"><b>{{ job.sourceLang.toUpperCase() }}</b> {{ lang(job.sourceLang) }}</span>
      <AppIcon name="arrow" :size="14" />
      <span class="lang"><b>{{ job.targetLang.toUpperCase() }}</b> {{ lang(job.targetLang) }}</span>
      <span class="cues mono">{{ job.cueCount }} cues</span>
    </p>
  </section>
</template>

<style scoped>
.card {
  display: grid;
  gap: 10px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.head {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: var(--primary-tint);
  color: var(--primary);
}

.name {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.specs {
  font-size: 11px;
  color: var(--text-muted);
}

.route {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--surface-subdued);
  font-size: 13px;
  color: var(--text-secondary);
}

.lang b {
  margin-right: 4px;
  color: var(--text);
}

.cues {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}
</style>
