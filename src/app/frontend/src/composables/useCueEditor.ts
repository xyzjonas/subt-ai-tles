import { computed, reactive, ref, watch, type Ref } from "vue";
import { listCues, retranslateCue, updateCue } from "../api/cues";
import { getJob } from "../api/jobs";
import type { Cue, CueVariant, Job } from "../api/types";
import { describeError } from "../i18n/apiErrors";
import { cps } from "../utils/srt";

export type CueFilter = "all" | "modified" | "flagged" | "cps";
export const CPS_LIMIT = 17;
const PAGE_SIZE = 50;

export interface EditorCue extends Cue {
  /** Target as originally translated by the model. */
  aiTarget: string;
  flagged: boolean;
  /** Proposed replacement (picked variant or manual edit), not stored until accepted. */
  draft?: string;
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
  const saving = reactive<Record<number, "saving" | "error">>({});
  /** Localized reason of the last failed retranslate / save of a cue. */
  const problems = reactive<Record<number, string>>({});

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      const [j, raw] = await Promise.all([getJob(jobId.value), listCues(jobId.value)]);
      job.value = j;
      cues.value = raw.map((c) => ({ ...c, aiTarget: c.target, flagged: false }));
      for (const key of Object.keys(variants)) delete variants[Number(key)];
      for (const key of Object.keys(status)) delete status[Number(key)];
      for (const key of Object.keys(saving)) delete saving[Number(key)];
      for (const key of Object.keys(problems)) delete problems[Number(key)];
    } catch (e) {
      error.value = describeError(e, "editor.loadFailed");
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

  /** Stages `text` on the cue; it only differs from the stored translation if it is a real change. */
  function propose(cue: EditorCue, text: string) {
    if (!text) return;
    cue.draft = text === cue.target ? undefined : text;
    delete saving[cue.index];
  }

  async function accept(cue: EditorCue) {
    if (cue.draft === undefined) return;
    saving[cue.index] = "saving";
    try {
      const stored = await updateCue(jobId.value, cue.index, cue.draft);
      cue.target = stored.target;
      cue.modifiedAt = cue.target === cue.aiTarget ? undefined : Date.now();
      cue.draft = undefined;
      delete saving[cue.index];
    } catch (e) {
      problems[cue.index] = describeError(e, "errors.unknown");
      saving[cue.index] = "error";
    }
  }

  function discard(cue: EditorCue) {
    cue.draft = undefined;
    delete saving[cue.index];
  }

  async function retranslate(cue: EditorCue, prompt?: string) {
    status[cue.index] = "loading";
    delete problems[cue.index];
    try {
      const fresh = await retranslateCue(jobId.value, cue.index, prompt);
      variants[cue.index] = prompt ? [...(variants[cue.index] ?? []), ...fresh] : fresh;
      delete status[cue.index];
    } catch (e) {
      problems[cue.index] = describeError(e, "errors.unknown");
      status[cue.index] = "error";
    }
  }

  const dismiss = (cue: EditorCue) => {
    delete variants[cue.index];
    delete status[cue.index];
    delete problems[cue.index];
  };

  const pending = computed(() => cues.value.filter((c) => c.draft !== undefined).length);
  const toggleFlag = (cue: EditorCue) => (cue.flagged = !cue.flagged);
  const showMore = () => (limit.value += PAGE_SIZE);

  return { job, cues, loading, error, query, filter, counts, visible, remaining, runningTime, variants, status, saving, problems, pending, load, propose, accept, discard, retranslate, dismiss, toggleFlag, showMore };
}
