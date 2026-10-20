<script setup lang="ts">
import { useUsage } from "../../composables/useUsage";
import QuotaMeter from "./QuotaMeter.vue";
import UsageSummary from "./UsageSummary.vue";
import UsageTable from "./UsageTable.vue";

/** Show this user's usage instead of your own (admin only). */
const props = defineProps<{ userId?: number }>();

const { summary, records, period, buckets, current, loading, loadingMore, hasMore, error, loadMore } = useUsage(props.userId);
</script>

<template>
  <div class="usage">
    <p v-if="loading" class="status" role="status">{{ $t("loading") }}</p>
    <p v-else-if="error && !summary" class="status" role="alert">{{ error }}</p>
    <template v-else-if="summary">
      <QuotaMeter :quota="summary.quota" />
      <UsageSummary v-model="period" :buckets="buckets" :current="current" />
      <UsageTable :records="records" :has-more="hasMore" :loading-more="loadingMore" @more="loadMore" />
      <p v-if="error" class="status" role="alert">{{ error }}</p>
    </template>
  </div>
</template>

<style scoped>
.usage {
  display: grid;
  gap: 24px;
}

.status {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}
</style>
