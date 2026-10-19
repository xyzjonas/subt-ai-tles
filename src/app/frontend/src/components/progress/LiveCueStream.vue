<script setup lang="ts">
import { computed } from "vue";
import type { Cue } from "../../api/types";
import { formatTimecode } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";

const props = defineProps<{ cue?: Cue }>();

const duration = computed(() => props.cue && ((props.cue.end - props.cue.start) / 1000).toFixed(2));
</script>

<template>
  <section class="card" aria-labelledby="stream-title">
    <header class="head">
      <h2 id="stream-title"><AppIcon name="terminal" :size="16" /> Live Stream Streamer</h2>
      <span v-if="cue" class="badge mono">Cue #{{ cue.index }}</span>
    </header>

    <p v-if="!cue" class="empty">Waiting for the first translated line…</p>
    <div v-else class="cue" aria-live="polite">
      <p class="time mono">
        <time>{{ formatTimecode(cue.start) }}</time> ➔ <time>{{ formatTimecode(cue.end) }}</time>
        <span>{{ duration }}s duration</span>
      </p>
      <p class="src"><small class="mono">SRC</small> <q>{{ cue.source }}</q></p>
      <p class="tgt"><small class="mono">TGT</small> <span>{{ cue.target }}<span class="cursor" aria-hidden="true">█</span></span></p>
    </div>
  </section>
</template>

<style scoped>
.card {
  display: grid;
  gap: 12px;
  padding: 16px;
  background: var(--canvas);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h2 {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

.badge {
  padding: 3px 10px;
  border-radius: var(--radius-tag);
  background: var(--primary-tint);
  color: var(--primary);
  font-size: 11px;
  font-weight: 600;
}

.empty {
  font-size: 13px;
  color: var(--text-muted);
}

.cue {
  display: grid;
  gap: 8px;
}

.time {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.time span {
  margin-left: auto;
  color: var(--text-muted);
}

.src,
.tgt {
  display: grid;
  grid-template-columns: 32px 1fr;
  align-items: baseline;
  font-size: 14px;
}

small {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-placeholder);
}

.src {
  font-style: italic;
  color: var(--text-secondary);
}

.tgt {
  font-weight: 700;
  color: var(--text);
}

.cursor {
  margin-left: 2px;
  color: var(--primary);
  animation: blink 1s steps(1) infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cursor {
    animation: none;
  }
}
</style>
