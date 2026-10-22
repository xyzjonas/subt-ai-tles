<script setup lang="ts">
import type { Messages } from "../../i18n/en";
import PreviewCueCard from "./PreviewCueCard.vue";
import PreviewIcon from "./PreviewIcon.vue";
import PreviewSummary from "./PreviewSummary.vue";
import { PREVIEW_CUES } from "./previewData";

const TOTAL_LINES = 1426;
// Counts shown on the filter pills of the full file, not of the three cues below.
const FILTERS = [
  { id: "all", count: TOTAL_LINES },
  { id: "modified", count: 3 },
  { id: "flagged", count: 1 },
  { id: "cps", count: 12 },
] as const;

defineProps<{ t: Messages["preview"]; locale: string }>();
</script>

<template>
  <section class="window" :aria-label="t.ariaLabel">
    <header class="chrome">
      <span class="dots" aria-hidden="true"><i /><i /><i /></span>
      <span class="address">{{ t.address }}</span>
    </header>

    <div class="page">
      <p class="back"><PreviewIcon name="back" :size="14" /> {{ t.back }}</p>

      <PreviewSummary :t="t.summary" :locale="locale" :lines="TOTAL_LINES" />

      <label class="search">
        <PreviewIcon name="search" :size="18" />
        <input type="search" :placeholder="t.search.placeholder" :aria-label="t.search.label" />
        <kbd>⌘K</kbd>
      </label>

      <div class="filters" role="group" :aria-label="t.filters.label">
        <span v-for="f in FILTERS" :key="f.id" class="pill" :class="{ active: f.id === 'all' }">
          {{ t.filters[f.id] }} ({{ f.count.toLocaleString(locale) }})
        </span>
      </div>

      <ul class="cues">
        <li v-for="cue in PREVIEW_CUES" :key="cue.index">
          <PreviewCueCard :cue="cue" :t="t" :locale="locale" />
        </li>
      </ul>
    </div>

    <footer class="action-bar">
      <span class="download"><PreviewIcon name="check" :size="18" /> {{ t.actionBar.download }}</span>
      <span class="sync" role="img" :aria-label="t.actionBar.sync"><PreviewIcon name="sync" :size="16" /></span>
    </footer>
  </section>
</template>

<style scoped>
.window {
  container-type: inline-size;
  max-width: 56rem;
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 1rem;
  background: var(--canvas);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
  text-align: left;
}
.chrome {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.dots {
  display: flex;
  gap: 6px;
}
.dots i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dots i:nth-child(1) { background: #f87171; }
.dots i:nth-child(2) { background: #fbbf24; }
.dots i:nth-child(3) { background: #4ade80; }
.address {
  flex: 1;
  max-width: 20rem;
  margin: 0 auto;
  padding: 3px 12px;
  border-radius: 9999px;
  background: var(--surface-subdued);
  font-family: var(--font-mono);
  font-size: 12px;
  text-align: center;
  color: var(--text-muted);
}

.page {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  padding: 20px;
}
@container (min-width: 600px) {
  .page {
    padding: 24px 32px;
  }
}
.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  justify-self: start;
  font-size: 13px;
  font-weight: 500;
  color: var(--primary);
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-placeholder);
}
.search:focus-within {
  outline: 2px solid var(--primary);
}
.search input {
  flex: 1;
  min-width: 0;
  padding: 10px 0;
  border: 0;
  outline: 0;
  background: none;
  font: inherit;
  font-size: 14px;
  color: var(--text);
}
kbd {
  padding: 2px 6px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface-subdued);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
}

.filters {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}
.pill {
  display: inline-flex;
  align-items: center;
  height: 36px;
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  color: var(--text-secondary);
}
.pill.active {
  background: var(--primary-tint);
  border-color: var(--primary);
  font-weight: 600;
  color: var(--primary);
}

.cues {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.92);
}
@container (min-width: 600px) {
  .action-bar {
    padding: 16px 32px;
  }
}
.download {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--primary);
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
  font-size: 15px;
  font-weight: 700;
  color: #fff;
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
</style>
