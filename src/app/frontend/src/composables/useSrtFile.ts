import { computed, ref } from "vue";
import { detectLanguage } from "../api/languages";
import { t } from "../i18n";
import { parseSrt } from "../utils/srt";

export function useSrtFile() {
  const file = ref<File | null>(null);
  const cueCount = ref(0);
  const detectedLang = ref<string | null>(null);
  const error = ref("");
  const loading = ref(false);

  async function select(candidate: File) {
    error.value = "";
    loading.value = true;
    try {
      const info = await parseSrt(candidate);
      file.value = candidate;
      cueCount.value = info.cueCount;
      detectedLang.value = await detectLanguage(candidate);
    } catch (e) {
      clear();
      error.value = e instanceof Error ? e.message : t("translate.file.unreadable");
    } finally {
      loading.value = false;
    }
  }

  function clear() {
    file.value = null;
    cueCount.value = 0;
    detectedLang.value = null;
  }

  return { file, cueCount, detectedLang, error, loading, hasFile: computed(() => !!file.value), select, clear };
}
