import { computed, onScopeDispose, ref, watch, type Ref } from "vue";
import { getCue } from "../api/cues";
import { cancelJob, getJob } from "../api/jobs";
import type { Cue, Job } from "../api/types";

const POLL_MS = 1500;
const CHUNK_SIZE = 30;

export type MilestoneState = "done" | "active" | "pending";

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
    const started = processed.value > 0;
    const finished = job.value?.status === "ready";
    return [
      { title: "Parsing SRT timecodes & syntax", detail: `Validated ${total.value} timecodes`, state: "done" },
      { title: "Contextual idiom & dialogue analysis", detail: "Character mapping confirmed", state: started ? "done" : "active" },
      {
        title: "Generating localized translation",
        detail: finished ? `Translated all ${total.value} lines` : started ? `Translating lines ${chunkStart.value}-${chunkEnd.value} of ${total.value}…` : "Waiting for analysis",
        state: finished ? "done" : started ? "active" : "pending",
      },
      { title: "Timecode calibration & SRT compilation", detail: finished ? "Compiled" : "Pending target completion", state: finished ? "done" : "pending" },
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
