<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { UsageBucket } from "../../api/types";
import { formatCredits, formatTokens, periodLabel, type UsagePeriod } from "../../utils/usage";
import SegmentedTabs from "../ui/SegmentedTabs.vue";

const period = defineModel<UsagePeriod>({ required: true });
const props = defineProps<{
  buckets: UsageBucket[];
  current: Record<UsagePeriod, UsageBucket | undefined>;
}>();

const { t } = useI18n();

const PERIOD_KEYS: UsagePeriod[] = ["day", "week", "month"];
const PERIODS = computed(() => PERIOD_KEYS.map((value) => ({ value, label: t(`dashboard.summary.periods.${value}`) })));

const peak = computed(() => Math.max(1, ...props.buckets.map((b) => b.credits)));
</script>

<template>
  <section class="summary" aria-labelledby="summary-title">
    <h2 id="summary-title">{{ t("dashboard.summary.title") }}</h2>

    <dl class="headlines">
      <div v-for="key in PERIOD_KEYS" :key="key">
        <dt>{{ t(`dashboard.summary.headlines.${key}`) }}</dt>
        <dd class="mono">{{ formatCredits(current[key]?.credits ?? 0) }}</dd>
        <dd class="tokens mono">{{ t("dashboard.summary.tokens", { n: formatTokens(current[key]?.tokens ?? 0) }) }}</dd>
      </div>
    </dl>

    <SegmentedTabs v-model="period" :tabs="PERIODS" :label="t('dashboard.summary.periodLabel')" />

    <table>
      <caption class="sr-only">{{ t(`dashboard.summary.caption.${period}`) }}</caption>
      <thead>
        <tr>
          <th scope="col">{{ t("dashboard.summary.period") }}</th>
          <th scope="col" class="num">{{ t("dashboard.summary.requests") }}</th>
          <th scope="col" class="num">{{ t("dashboard.summary.tokensColumn") }}</th>
          <th scope="col" class="num">{{ t("dashboard.summary.credits") }}</th>
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
