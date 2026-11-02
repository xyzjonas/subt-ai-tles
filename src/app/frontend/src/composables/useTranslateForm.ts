import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { createJob, estimateJob } from "../api/jobs";
import { listLanguages } from "../api/languages";
import { describeError } from "../i18n/apiErrors";
import type { JobEstimate, Language } from "../api/types";
import { useSrtFiles } from "./useSrtFiles";

const TARGET_KEY = "target-language";

export function useTranslateForm() {
  const router = useRouter();
  const srt = useSrtFiles();

  const languages = ref<Language[]>([]);
  const targetCode = ref(localStorage.getItem(TARGET_KEY) ?? "en");
  const estimate = ref<JobEstimate | null>(null);
  const submitting = ref(false);
  const submitError = ref("");

  const byCode = (code: string) => languages.value.find((l) => l.code === code);
  const target = computed(() => byCode(targetCode.value));
  const canSubmit = computed(() => srt.hasFiles.value && !!target.value && !submitting.value);

  onMounted(async () => {
    languages.value = await listLanguages();
    if (!byCode(targetCode.value)) targetCode.value = "en";
  });

  /** User-driven change, persisted for the next visit. */
  function setTarget(code: string) {
    targetCode.value = code;
    localStorage.setItem(TARGET_KEY, code);
  }

  watch(srt.totalCues, async (count) => {
    estimate.value = count ? await estimateJob(count) : null;
  });

  async function submit() {
    if (!canSubmit.value) return;
    submitting.value = true;
    submitError.value = "";
    const files = srt.entries.value.map((e) => e.file);
    try {
      const results = await Promise.allSettled(files.map((file) => createJob({ file, targetLang: targetCode.value })));
      const created = results.flatMap((r) => (r.status === "fulfilled" ? [r.value] : []));
      const failures = results.flatMap((r, i) =>
        r.status === "rejected" ? [`${files[i].name}: ${describeError(r.reason, "errors.unknown")}`] : [],
      );
      // Only failed files stay selected, so the user can retry them.
      srt.keepOnly(files.filter((_, i) => results[i].status === "rejected"));
      if (failures.length) {
        submitError.value = failures.join("\n");
        return;
      }
      await router.push(created.length === 1 ? { name: "job", params: { id: created[0].id } } : { name: "requests" });
    } finally {
      submitting.value = false;
    }
  }

  return { srt, languages, target, targetCode, estimate, submitting, submitError, canSubmit, setTarget, submit };
}
