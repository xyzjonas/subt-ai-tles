import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { createJob, estimateJob } from "../api/jobs";
import { listLanguages } from "../api/languages";
import { describeError } from "../i18n/apiErrors";
import type { JobEstimate, Language } from "../api/types";
import { useSrtFile } from "./useSrtFile";

const TARGET_KEY = "target-language";

export function useTranslateForm() {
  const router = useRouter();
  const srt = useSrtFile();

  const languages = ref<Language[]>([]);
  const targetCode = ref(localStorage.getItem(TARGET_KEY) ?? "en");
  const estimate = ref<JobEstimate | null>(null);
  const submitting = ref(false);
  const submitError = ref("");

  const byCode = (code: string) => languages.value.find((l) => l.code === code);
  const target = computed(() => byCode(targetCode.value));
  const canSubmit = computed(() => srt.hasFile.value && !!target.value && !submitting.value);

  onMounted(async () => {
    languages.value = await listLanguages();
    if (!byCode(targetCode.value)) targetCode.value = "en";
  });

  /** User-driven change, persisted for the next visit. */
  function setTarget(code: string) {
    targetCode.value = code;
    localStorage.setItem(TARGET_KEY, code);
  }

  watch(srt.cueCount, async (count) => {
    estimate.value = count ? await estimateJob(count) : null;
  });

  async function submit() {
    if (!canSubmit.value || !srt.file.value) return;
    submitting.value = true;
    submitError.value = "";
    try {
      const { id } = await createJob({
        file: srt.file.value,
        targetLang: targetCode.value,
      });
      await router.push({ name: "job", params: { id } });
    } catch (e) {
      submitError.value = describeError(e, "errors.unknown");
    } finally {
      submitting.value = false;
    }
  }

  return { srt, languages, target, targetCode, estimate, submitting, submitError, canSubmit, setTarget, submit };
}
