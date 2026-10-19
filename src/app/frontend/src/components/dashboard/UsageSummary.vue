<script setup lang="ts">
import { computed } from "vue";
import type { UsageBucket } from "../../api/types";
import { formatCredits, formatTokens, periodLabel, type UsagePeriod } from "../../utils/usage";
import SegmentedTabs from "../ui/SegmentedTabs.vue";

const period = defineModel<UsagePeriod>({ required: true });
const props = defineProps<{
  buckets: UsageBucket[];
  current: Record<UsagePeriod, UsageBucket | undefined>;
}>();

const PERIODS: { value: UsagePeriod; label: string }[] = [
  { value: "day", label: "Daily" },
  { value: "week", label: "Weekly" },
  { value: "month", label: "Monthly" },
];

const HEADLINES: { period: UsagePeriod; label: string }[] = [
  { period: "day", label: "Today" },
  { period: "week", label: "This week" },
  { period: "month", label: "This month" },
];

const peak = computed(() => Math.max(1, ...props.buckets.map((b) => b.credits)));
</script>

<template>
  <section class="summary" aria-labelledby="summary-title">
    <h2 id="summary-title">Spending</h2>

    <dl class="headlines">
      <div v-for="h in HEADLINES" :key="h.period">
        <dt>{{ h.label }}</dt>
        <dd class="mono">{{ formatCredits(current[h.period]?.credits ?? 0) }}</dd>
        <dd class="tokens mono">{{ formatTokens(current[h.period]?.tokens ?? 0) }} tokens</dd>
      </div>
    </dl>

    <SegmentedTabs v-model="period" :tabs="PERIODS" label="Summary period" />

    <table>
      <caption class="sr-only">Credits spent per {{ period }}</caption>
      <thead>
        <tr>
          <th scope="col">Period</th>
          <th scope="col" class="num">Requests</th>
          <th scope="col" class="num">Tokens</th>
          <th scope="col" class="num">Credits</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in buckets" :key="b.start" :class="{ idle: !b.requests }">
          <th scope="row">
            {{ periodLabel(b.start, period) }}
            <span class="bar" aria-hidden="true" :style="{ width: `${(b.credits / peak) * 100}%` }" />
          </th>
          <td class="num mono">{{ b.requests }}</td>
          <td class="num mono">{{ formatTokens(b.tokens) }}</td>
          <td class="num mono">{{ formatCredits(b.credits) }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.summary {
  display: grid;
  gap: 14px;
}

h2 {
  font-size: 16px;
  font-weight: 600;
}

.headlines {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.headlines div {
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

dt {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

dd {
  margin: 0;
}

dd.mono:not(.tokens) {
  font-size: 20px;
  font-weight: 500;
}

.tokens {
  font-size: 11px;
  color: var(--text-muted);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  font-size: 13px;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-soft);
  text-align: left;
}

thead th {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

tbody th {
  position: relative;
  font-weight: 500;
}

.num {
  text-align: right;
}

.idle {
  color: var(--text-placeholder);
}

.bar {
  position: absolute;
  inset: auto auto 0 0;
  height: 2px;
  background: var(--primary);
  opacity: 0.5;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
</style>
