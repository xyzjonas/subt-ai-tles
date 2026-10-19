<script setup lang="ts">
import type { UsageRecord } from "../../api/types";
import { formatWhen } from "../../utils/srt";
import { KIND_LABEL, formatCredits, formatTokens } from "../../utils/usage";

defineProps<{ records: UsageRecord[]; hasMore: boolean; loadingMore: boolean }>();
defineEmits<{ more: [] }>();
</script>

<template>
  <section class="records" aria-labelledby="records-title">
    <h2 id="records-title">Requests</h2>

    <p v-if="!records.length" class="empty">No requests yet. Translate a file to see its usage here.</p>
    <template v-else>
      <div class="scroll">
        <table>
          <thead>
            <tr>
              <th scope="col">When</th>
              <th scope="col">Type</th>
              <th scope="col">Model</th>
              <th scope="col" class="num">Prompt</th>
              <th scope="col" class="num">Completion</th>
              <th scope="col" class="num">Credits</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>
                <time :datetime="r.createdAt">{{ formatWhen(r.createdAt) }}</time>
              </td>
              <td>{{ KIND_LABEL[r.kind] }}</td>
              <td class="mono">{{ r.model }}</td>
              <td class="num mono">{{ formatTokens(r.promptTokens) }}</td>
              <td class="num mono">{{ formatTokens(r.completionTokens) }}</td>
              <td class="num mono">{{ formatCredits(r.credits) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <button v-if="hasMore" type="button" class="more" :disabled="loadingMore" @click="$emit('more')">
        {{ loadingMore ? "Loading…" : "Show more" }}
      </button>
    </template>
  </section>
</template>

<style scoped>
.records {
  display: grid;
  gap: 14px;
}

h2 {
  font-size: 16px;
  font-weight: 600;
}

.scroll {
  overflow-x: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  white-space: nowrap;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-soft);
  text-align: left;
}

tbody tr:last-child td {
  border-bottom: 0;
}

thead th {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.num {
  text-align: right;
}

.empty {
  padding: 24px 0;
  text-align: center;
  color: var(--text-muted);
}

.more {
  height: 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
}

.more:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
