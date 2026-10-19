<script setup lang="ts">
import { computed, ref } from "vue";
import { downloadJob } from "../../api/jobs";
import type { Job } from "../../api/types";
import { stageLabel } from "../../utils/stage";
import { downloadBlob, formatWhen, timeAgo, translatedFileName } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

const props = defineProps<{ job: Job }>();

const processing = computed(() => props.job.status === "processing");
const percent = computed(() => Math.round(((props.job.processedCues ?? 0) / props.job.cueCount) * 100));
const lang = (code: string) => new Intl.DisplayNames("en", { type: "language" }).of(code) ?? code;

const downloading = ref(false);
async function download() {
  downloading.value = true;
  try {
    downloadBlob(await downloadJob(props.job), translatedFileName(props.job));
  } finally {
    downloading.value = false;
  }
}
</script>

<template>
  <article class="card" :class="{ processing }">
    <RouterLink :to="{ name: job.status === 'ready' ? 'editor' : 'job', params: { id: job.id } }" class="link" :aria-label="`Open ${job.fileName}`" />
    <header class="head">
      <span class="icon"><AppIcon name="file" :size="18" /></span>
      <h3 class="name mono">{{ job.fileName }}</h3>
      <time class="when" :datetime="job.createdAt">{{ processing ? timeAgo(job.createdAt) : formatWhen(job.createdAt) }}</time>
    </header>

    <p class="route">
      <span class="lang-pill">
        {{ job.sourceLang.toUpperCase() }} <AppIcon name="arrow" :size="12" /> {{ job.targetLang.toUpperCase() }} ({{ lang(job.targetLang) }})
      </span>
    </p>

    <template v-if="processing">
      <StatusBadge tone="warning" dot pulse>
        Processing {{ percent }}% • {{ job.processedCues }} / {{ job.cueCount }} lines
      </StatusBadge>
      <progress class="bar" :value="percent" max="100" :aria-label="`${percent}% translated`" />
      <p class="step mono"><AppIcon name="sync" :size="12" /> {{ stageLabel(job) }}</p>
    </template>

    <template v-else>
      <StatusBadge tone="success"><AppIcon name="check" :size="12" /> Completed • {{ job.cueCount }} lines</StatusBadge>
      <p v-if="job.model" class="step mono">Synced with {{ job.model }}</p>
      <button type="button" class="download" :disabled="downloading" @click="download">
        <AppIcon name="download" :size="14" /> {{ downloading ? "Preparing…" : "Download" }}
      </button>
    </template>

    <AppIcon class="chevron" name="next" :size="18" />
  </article>
</template>

<style scoped>
.card {
  position: relative;
  display: grid;
  gap: 10px;
  justify-items: start;
  padding: 16px 40px 16px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.card.processing {
  border-left: 4px solid var(--warning-strong);
}

.card:hover {
  border-color: var(--primary);
}

/* stretched link: whole card is clickable, inner button stays above it */
.link {
  position: absolute;
  inset: 0;
  border-radius: inherit;
}

.head {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-width: 0;
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

.name {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.when {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.lang-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-tag);
  background: #e0e7ff;
  color: #3730a3;
  font-size: 11px;
  font-weight: 600;
}

.bar {
  width: 100%;
  height: 4px;
  border: 0;
  border-radius: 4px;
  background: var(--surface-subdued);
  appearance: none;
}

.bar::-webkit-progress-bar {
  background: var(--surface-subdued);
  border-radius: 4px;
}

.bar::-webkit-progress-value {
  background: var(--warning-strong);
  border-radius: 4px;
}

.bar::-moz-progress-bar {
  background: var(--warning-strong);
  border-radius: 4px;
}

.step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
}

.download {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.download:hover:not(:disabled) {
  background: var(--primary-hover);
}

.download:disabled {
  opacity: 0.7;
  cursor: progress;
}

.chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  translate: 0 -50%;
  color: var(--text-placeholder);
}
</style>
