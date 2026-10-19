import { computed, onMounted, ref } from "vue";
import { getUsage, listUsageRecords } from "../api/usage";
import type { UsageBucket, UsageRecord, UsageSummary } from "../api/types";
import type { UsagePeriod } from "../utils/usage";

const PAGE_SIZE = 50;

export function useUsage() {
  const summary = ref<UsageSummary | null>(null);
  const records = ref<UsageRecord[]>([]);
  const period = ref<UsagePeriod>("day");
  const loading = ref(true);
  const loadingMore = ref(false);
  const hasMore = ref(false);
  const error = ref("");

  onMounted(async () => {
    try {
      const [usage, page] = await Promise.all([getUsage(), listUsageRecords(PAGE_SIZE, 0)]);
      summary.value = usage;
      records.value = page;
      hasMore.value = page.length === PAGE_SIZE;
    } catch {
      error.value = "Could not load your usage.";
    } finally {
      loading.value = false;
    }
  });

  async function loadMore() {
    loadingMore.value = true;
    try {
      const page = await listUsageRecords(PAGE_SIZE, records.value.length);
      records.value.push(...page);
      hasMore.value = page.length === PAGE_SIZE;
    } catch {
      error.value = "Could not load more requests.";
    } finally {
      loadingMore.value = false;
    }
  }

  /** Buckets of the selected period, newest first. */
  const buckets = computed<UsageBucket[]>(() => {
    if (!summary.value) return [];
    const { daily, weekly, monthly } = summary.value;
    return [...{ day: daily, week: weekly, month: monthly }[period.value]].reverse();
  });

  /** Totals of the current day, week and month (the newest bucket of each). */
  const newest = (list?: UsageBucket[]) => list?.[list.length - 1];
  const current = computed(() => ({
    day: newest(summary.value?.daily),
    week: newest(summary.value?.weekly),
    month: newest(summary.value?.monthly),
  }));

  return { summary, records, period, buckets, current, loading, loadingMore, hasMore, error, loadMore };
}
