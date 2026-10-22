<script setup lang="ts">
import type { Messages } from "../../i18n/en";
import PreviewBadge from "./PreviewBadge.vue";
import PreviewIcon from "./PreviewIcon.vue";
import { plural } from "./previewData";

const props = defineProps<{ t: Messages["preview"]["summary"]; locale: string; lines: number }>();

const cells = [
  { label: props.t.pair, value: props.t.pairValue },
  { label: props.t.density, value: plural(props.locale, props.t.lines, props.lines) },
  { label: props.t.runningTime, value: props.t.runningTimeValue },
  { label: props.t.completed, value: props.t.completedValue },
];
</script>

<template>
  <section class="summary" :aria-label="t.label">
    <header class="head">
      <span class="icon"><PreviewIcon name="file" :size="18" /></span>
      <div class="file">
        <h2 class="name mono">{{ t.fileName }}</h2>
        <p class="model mono">{{ t.model }} • {{ t.confidence }}</p>
      </div>
      <PreviewBadge tone="success"><PreviewIcon name="check" :size="12" /> {{ t.ready }}</PreviewBadge>
    </header>

    <dl class="matrix">
      <div v-for="c in cells" :key="c.label">
        <dt class="section-label">{{ c.label.toLocaleUpperCase(locale) }}</dt>
        <dd>{{ c.value }}</dd>
      </div>
    </dl>

    <div class="actions">
      <span class="primary"><PreviewIcon name="download" :size="16" /> {{ t.download }}</span>
      <span class="icon-btn" role="img" :aria-label="t.copy"><PreviewIcon name="copy" :size="16" /></span>
    </div>
  </section>
</template>

<style scoped>
.summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
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
  overflow: hidden;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.model {
  font-size: 11px;
  color: var(--text-muted);
}
.mono {
  font-family: var(--font-mono);
  font-weight: 500;
}
.section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
.matrix {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
  padding: 12px;
  background: var(--surface-subdued);
  border-radius: var(--radius-md);
}
@container (min-width: 600px) {
  .matrix {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
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
  border-radius: var(--radius-md);
  background: var(--primary);
  font-weight: 600;
  color: #fff;
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
</style>
