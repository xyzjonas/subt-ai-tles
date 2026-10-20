import { computed, onMounted, onUnmounted, ref } from "vue";
import { listJobs } from "../api/jobs";
import type { Job } from "../api/types";
import { timeAgo, formatWhen } from "../utils/srt";

export type RequestTab = "processing" | "completed";

export function useRequests() {
  const jobs = ref<Job[]>([]);
  const query = ref("");
  const tab = ref<RequestTab>("processing");
  const loading = ref(true);

  onMounted(async () => {
    jobs.value = await listJobs();
    loading.value = false;
    if (!jobs.value.some((j) => j.status === "processing")) tab.value = "completed";
  });

  const inTab = (job: Job, t: RequestTab) => (t === "processing" ? job.status === "processing" : job.status !== "processing");

  const counts = computed(() => ({
    processing: jobs.value.filter((j) => inTab(j, "processing")).length,
    completed: jobs.value.filter((j) => inTab(j, "completed")).length,
  }));

  const visible = computed(() => {
    const q = query.value.trim().toLowerCase();
    return jobs.value
      .filter((j) => inTab(j, tab.value))
      .filter((j) => !q || [j.fileName, j.sourceLang ?? "", j.targetLang, timeAgo(j.createdAt), formatWhen(j.createdAt)].some((f) => f.toLowerCase().includes(q)));
  });

  return { jobs, query, tab, loading, counts, visible };
}
