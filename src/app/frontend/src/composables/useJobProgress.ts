import { computed, onScopeDispose, ref, watch, type Ref } from "vue";
import { getCue } from "../api/cues";
import { cancelJob, getJob } from "../api/jobs";
import type { Cue, Job, JobStage, SummaryStatus } from "../api/types";

const POLL_MS = 1500;
const CHUNK_SIZE = 30;

export type MilestoneState = "done" | "active" | "pending" | "skipped";

const STAGES: JobStage[] = ["recognizing", "summarizing", "translating"];
const BRIEF_DETAIL: Record<SummaryStatus, string> = {
  generated: "Story brief written",
  stored: "Reused saved story brief",
  skipped: "Title not recognized, no brief needed",
  failed: "Couldn't write a brief, continuing without",
};

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
        title: "Uploading & recognizing",
        detail: at("recognizing") === "active" ? "Reading the file and looking up the title…" : brief === "skipped" ? "Title not recognized" : "Title recognized",
        state: at("recognizing"),
      },
      {
        title: "Summarizing",
        detail: briefState === "pending" ? "Waiting for the title lookup" : briefState === "active" ? "Reading the whole script for context…" : BRIEF_DETAIL[brief ?? "skipped"],
        state: briefState === "done" && (brief === "skipped" || brief === "failed") ? "skipped" : briefState,
      },
      {
        title: "Translating cues",
        detail: finished ? `Translated all ${total.value} lines` : stage === "translating" ? `Translating lines ${chunkStart.value}-${chunkEnd.value} of ${total.value}…` : "Waiting for the story summary",
        state: at("translating"),
      },
      { title: "Done", detail: finished ? "Ready to review" : "Pending translation", state: finished ? "done" : "pending" },
    ];
  });

  async function poll() {
    try {
      const fresh = await getJob(jobId.value);
      job.value = fresh;
      error.value = "";
      if (fresh.status === "ready") return onComplete();
      if (fresh.status === "failed") return (error.value = fresh.error ?? "This translation failed.");
      if (fresh.processedCues) cue.value = await getCue(jobId.value, fresh.processedCues);
    } catch {
      error.value = "We couldn't load this request.";
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
