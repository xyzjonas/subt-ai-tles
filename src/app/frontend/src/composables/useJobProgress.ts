import { computed, onScopeDispose, ref, watch, type Ref } from "vue";
import { getCue } from "../api/cues";
import { cancelJob, getJob } from "../api/jobs";
import type { Cue, Job, JobStage } from "../api/types";
import { t } from "../i18n";
import { describeCode } from "../i18n/apiErrors";

const POLL_MS = 1500;
const CHUNK_SIZE = 30;

export type MilestoneState = "done" | "active" | "pending" | "skipped";

const STAGES: JobStage[] = ["recognizing", "summarizing", "translating"];

/** Polls a processing job and derives gauge, milestone and live-cue state from it. */
export function useJobProgress(jobId: Ref<string>, onComplete: () => void) {
  const job = ref<Job>();
  const cue = ref<Cue>();
  const error = ref("");
  const cancelling = ref(false);
  let timer: ReturnType<typeof setTimeout> | undefined;

  const processed = computed(() => job.value?.processedCues ?? 0);
  const total = computed(() => job.value?.cueCount ?? 0);
  const percent = computed(() => (total.value ? Math.floor((processed.value / total.value) * 100) : 0));

  const chunkStart = computed(() => Math.floor(Math.max(0, processed.value - 1) / CHUNK_SIZE) * CHUNK_SIZE + 1);
  const chunkEnd = computed(() => Math.min(total.value, chunkStart.value + CHUNK_SIZE - 1));
  const chunkPercent = computed(() => Math.min(100, Math.round(((processed.value - chunkStart.value + 1) / CHUNK_SIZE) * 100)));

  const milestones = computed<{ title: string; detail: string; state: MilestoneState }[]>(() => {
    const finished = job.value?.status === "ready";
    const stage = job.value?.stage ?? "recognizing";
    const at = (target: JobStage) => (finished ? "done" : stage === target ? "active" : STAGES.indexOf(stage) > STAGES.indexOf(target) ? "done" : "pending") satisfies MilestoneState;
    const brief = job.value?.summaryStatus;
    const briefState = at("summarizing");

    return [
      {
        title: t("progress.milestones.recognize.title"),
        detail: t(`progress.milestones.recognize.${at("recognizing") === "active" ? "active" : brief === "skipped" ? "skipped" : "done"}`),
        state: at("recognizing"),
      },
      {
        title: t("progress.milestones.summarize.title"),
        detail: t(`progress.milestones.summarize.${briefState === "done" ? (brief ?? "skipped") : briefState}`),
        state: briefState === "done" && (brief === "skipped" || brief === "failed") ? "skipped" : briefState,
      },
      {
        title: t("progress.milestones.translate.title"),
        detail: finished
          ? t("progress.milestones.translate.done", { total: total.value })
          : stage === "translating"
            ? t("progress.milestones.translate.active", { from: chunkStart.value, to: chunkEnd.value, total: total.value })
            : t("progress.milestones.translate.pending"),
        state: at("translating"),
      },
      { title: t("progress.milestones.finish.title"), detail: t(`progress.milestones.finish.${finished ? "done" : "pending"}`), state: finished ? "done" : "pending" },
    ];
  });

  async function poll() {
    try {
      const fresh = await getJob(jobId.value);
      job.value = fresh;
      error.value = "";
      if (fresh.status === "ready") return onComplete();
      if (fresh.status === "failed") return (error.value = fresh.error ? describeCode(fresh.error) : t("progress.failedFallback"));
      if (fresh.processedCues) cue.value = await getCue(jobId.value, fresh.processedCues);
    } catch {
      error.value = t("progress.loadFailed");
    }
    timer = setTimeout(poll, POLL_MS);
  }

  async function cancel() {
    cancelling.value = true;
    clearTimeout(timer);
    try {
      await cancelJob(jobId.value);
      onComplete();
    } finally {
      cancelling.value = false;
    }
  }

  watch(jobId, () => { clearTimeout(timer); job.value = cue.value = undefined; poll(); }, { immediate: true });
  onScopeDispose(() => clearTimeout(timer));

  return { job, cue, error, cancelling, processed, total, percent, chunkPercent, milestones, retry: poll, cancel };
}
