import { computed, reactive, ref, watch, type Ref } from "vue";
import { listCues, retranslateCue } from "../api/cues";
import { getJob } from "../api/jobs";
import type { Cue, CueVariant, Job } from "../api/types";
import { cps } from "../utils/srt";

export type CueFilter = "all" | "modified" | "flagged" | "cps";
export const CPS_LIMIT = 17;
const PAGE_SIZE = 50;

export interface EditorCue extends Cue {
  /** Target as originally translated by the model. */
  aiTarget: string;
  flagged: boolean;
  modifiedAt?: number;
}

const FILTERS: Record<CueFilter, (c: EditorCue) => boolean> = {
  all: () => true,
  modified: (c) => c.modifiedAt !== undefined,
  flagged: (c) => c.flagged,
  cps: (c) => cps(c) > CPS_LIMIT,
};

export function useCueEditor(jobId: Ref<string>) {
  const job = ref<Job>();
  const cues = ref<EditorCue[]>([]);
  const loading = ref(true);
  const error = ref("");

  const query = ref("");
  const filter = ref<CueFilter>("all");
  const limit = ref(PAGE_SIZE);

  const variants = reactive<Record<number, CueVariant[]>>({});
  const status = reactive<Record<number, "loading" | "error">>({});

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      const [j, raw] = await Promise.all([getJob(jobId.value), listCues(jobId.value)]);
      job.value = j;
      cues.value = raw.map((c) => ({ ...c, aiTarget: c.target, flagged: false }));
      for (const key of Object.keys(variants)) delete variants[Number(key)];
      for (const key of Object.keys(status)) delete status[Number(key)];
    } catch {
      error.value = "We couldn't load this request.";
    } finally {
      loading.value = false;
    }
  }

  watch(jobId, load, { immediate: true });
  watch([query, filter], () => (limit.value = PAGE_SIZE));

  const counts = computed(() => ({
    all: cues.value.length,
    modified: cues.value.filter(FILTERS.modified).length,
    flagged: cues.value.filter(FILTERS.flagged).length,
    cps: cues.value.filter(FILTERS.cps).length,
  }));

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    const matches = (c: EditorCue) =>
      !q ||
      (q.startsWith("#") ? String(c.index).startsWith(q.slice(1)) : c.source.toLowerCase().includes(q) || c.target.toLowerCase().includes(q));
    return cues.value.filter((c) => FILTERS[filter.value](c) && matches(c));
  });

  const visible = computed(() => filtered.value.slice(0, limit.value));
  const remaining = computed(() => filtered.value.length - visible.value.length);
  const runningTime = computed(() => cues.value[cues.value.length - 1]?.end ?? 0);

  function setTarget(cue: EditorCue, text: string) {
    if (!text || text === cue.target) return;
    cue.target = text;
    cue.modifiedAt = Date.now();
  }

  async function retranslate(cue: EditorCue, prompt?: string) {
    status[cue.index] = "loading";
    try {
      const fresh = await retranslateCue(jobId.value, cue, prompt);
      variants[cue.index] = prompt ? [...(variants[cue.index] ?? []), ...fresh] : fresh;
      delete status[cue.index];
    } catch {
      status[cue.index] = "error";
    }
  }

  const dismiss = (cue: EditorCue) => {
    delete variants[cue.index];
    delete status[cue.index];
  };

  const toggleFlag = (cue: EditorCue) => (cue.flagged = !cue.flagged);
  const showMore = () => (limit.value += PAGE_SIZE);

  return { job, cues, loading, error, query, filter, counts, visible, remaining, runningTime, variants, status, load, setTarget, retranslate, dismiss, toggleFlag, showMore };
}
