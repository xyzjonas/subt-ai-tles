import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { createJob, estimateJob } from "../api/jobs";
import { listLanguages } from "../api/languages";
import type { JobEstimate, Language } from "../api/types";
import { useSrtFile } from "./useSrtFile";

const TARGET_KEY = "target-language";

export function useTranslateForm() {
  const router = useRouter();
  const srt = useSrtFile();

  const languages = ref<Language[]>([]);
  const sourceCode = ref("en");
  const targetCode = ref(localStorage.getItem(TARGET_KEY) ?? "en");
  const estimate = ref<JobEstimate | null>(null);
  const submitting = ref(false);
  const submitError = ref("");

  const byCode = (code: string) => languages.value.find((l) => l.code === code);
  const source = computed(() => byCode(sourceCode.value));
  const target = computed(() => byCode(targetCode.value));
  const canSubmit = computed(() => srt.hasFile.value && !!target.value && sourceCode.value !== targetCode.value && !submitting.value);

  onMounted(async () => {
    languages.value = await listLanguages();
    if (!byCode(targetCode.value)) targetCode.value = "en";
  });


  watch(srt.detectedLang, (code) => {
    if (!code) return;
    sourceCode.value = code;
    if (targetCode.value === code) targetCode.value = languages.value.find((l) => l.code !== code)?.code ?? targetCode.value;
  });

  /** User-driven change: persisted, unlike the automatic switch on language detection. */
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
        sourceLang: sourceCode.value,
        targetLang: targetCode.value,
      });
      await router.push({ name: "job", params: { id } });
    } catch {
      submitError.value = "Could not start the translation. Please try again.";
    } finally {
      submitting.value = false;
    }
  }

  return { srt, languages, source, target, sourceCode, targetCode, estimate, submitting, submitError, canSubmit, setTarget, submit };
}
