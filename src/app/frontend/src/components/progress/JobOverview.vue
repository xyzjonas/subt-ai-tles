<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { Job } from "../../api/types";
import { displayLanguage } from "../../utils/language";
import { timeAgo } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ job: Job }>();

const { t, locale } = useI18n();
const lang = (code: string) => displayLanguage(code, locale.value) ?? code;
</script>

<template>
  <section class="card" :aria-label="t('progress.overview.label')">
    <header class="head">
      <span class="icon"><AppIcon name="file" :size="18" /></span>
      <h2 class="name mono">{{ job.fileName }}</h2>
      <StatusBadge tone="success" dot pulse>{{ t("progress.overview.live") }}</StatusBadge>
    </header>
    <p class="specs mono">{{ t("progress.overview.specs", { ago: timeAgo(job.createdAt) }) }}</p>

    <p class="route">
      <template v-if="job.sourceLang">
        <span class="lang"><b>{{ job.sourceLang.toUpperCase() }}</b> {{ lang(job.sourceLang) }}</span>
        <AppIcon name="arrow" :size="14" />
      </template>
      <span class="lang"><b>{{ job.targetLang.toUpperCase() }}</b> {{ lang(job.targetLang) }}</span>
      <span class="cues mono">{{ t("cues", { count: job.cueCount }, job.cueCount) }}</span>
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
