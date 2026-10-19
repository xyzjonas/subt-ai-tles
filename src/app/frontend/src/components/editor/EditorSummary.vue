<script setup lang="ts">
import { computed } from "vue";
import type { Job } from "../../api/types";
import { formatRunningTime, formatWhen } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

const props = defineProps<{ job: Job; lines: number; runningTime: number; copied: boolean; canShare: boolean }>();
defineEmits<{ download: []; copy: []; share: [] }>();

const language = computed(() => new Intl.DisplayNames("en", { type: "language" }).of(props.job.targetLang) ?? props.job.targetLang);
const cells = computed(() => [
  { label: "Linguistic pair", value: `${props.job.sourceLang.toUpperCase()} → ${props.job.targetLang.toUpperCase()} (${language.value})` },
  { label: "Density & cues", value: `${props.lines.toLocaleString()} lines` },
  { label: "Running time", value: formatRunningTime(props.runningTime) },
  { label: "Completed", value: formatWhen(props.job.createdAt) },
]);
</script>

<template>
  <section class="summary" aria-label="File summary">
    <header class="head">
      <span class="icon"><AppIcon name="file" :size="18" /></span>
      <div class="file">
        <h2 class="name mono">{{ job.fileName }}</h2>
        <p class="model mono">
          <template v-if="job.model">Model: {{ job.model }}</template>
          <template v-if="job.confidence"> • {{ job.confidence }}% confident</template>
        </p>
      </div>
      <StatusBadge tone="success"><AppIcon name="check" :size="12" /> Ready</StatusBadge>
    </header>

    <dl class="matrix">
      <div v-for="c in cells" :key="c.label" class="cell">
        <dt class="section-label">{{ c.label.toUpperCase() }}</dt>
        <dd>{{ c.value }}</dd>
      </div>
    </dl>

    <div class="actions">
      <button type="button" class="primary" @click="$emit('download')"><AppIcon name="download" :size="16" /> Download .SRT</button>
      <button type="button" class="icon-btn" :aria-label="copied ? 'Copied' : 'Copy SRT to clipboard'" @click="$emit('copy')">
        <AppIcon :name="copied ? 'check' : 'copy'" :size="16" />
      </button>
      <button v-if="canShare" type="button" class="icon-btn" aria-label="Share" @click="$emit('share')">
        <AppIcon name="share" :size="16" />
      </button>
    </div>
  </section>
</template>

<style scoped>
.summary {
  display: grid;
  gap: 16px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.head {
  display: flex;
  align-items: center;
  gap: 10px;
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

.file {
  flex: 1;
  min-width: 0;
}

.name {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model {
  font-size: 11px;
  color: var(--text-muted);
}

.matrix {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 0;
  padding: 12px;
  background: var(--surface-subdued);
  border-radius: var(--radius-md);
}

dd {
  margin: 2px 0 0;
  font-size: 13px;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
}

.primary {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 40px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: #fff;
  font-weight: 600;
}

.primary:hover {
  background: var(--primary-hover);
}

.icon-btn {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  color: var(--text-secondary);
}

.icon-btn:hover {
  background: var(--border);
}
</style>
