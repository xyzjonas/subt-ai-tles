import { computed, onMounted, ref } from "vue";
import { getUsage, listUsageRecords } from "../api/usage";
import type { UsageBucket, UsageRecord, UsageSummary } from "../api/types";
import { t } from "../i18n";
import type { UsagePeriod } from "../utils/usage";

const PAGE_SIZE = 50;

/** Usage of the signed-in user, or of the user with `userId` (admin only). */
export function useUsage(userId?: number) {
  const summary = ref<UsageSummary | null>(null);
  const records = ref<UsageRecord[]>([]);
  const period = ref<UsagePeriod>("day");
  const loading = ref(true);
  const loadingMore = ref(false);
  const hasMore = ref(false);
  const error = ref("");

  onMounted(async () => {
    try {
      const [usage, page] = await Promise.all([getUsage(userId), listUsageRecords(PAGE_SIZE, 0, userId)]);
      summary.value = usage;
      records.value = page;
      hasMore.value = page.length === PAGE_SIZE;
    } catch {
      error.value = t(userId === undefined ? "dashboard.usageLoadFailed" : "dashboard.userUsageLoadFailed");
    } finally {
      loading.value = false;
    }
  });

  async function loadMore() {
    loadingMore.value = true;
    try {
      const page = await listUsageRecords(PAGE_SIZE, records.value.length, userId);
      records.value.push(...page);
      hasMore.value = page.length === PAGE_SIZE;
    } catch {
      error.value = t("dashboard.moreLoadFailed");
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
