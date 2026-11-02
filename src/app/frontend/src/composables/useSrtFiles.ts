import { computed, ref } from "vue";
import { t } from "../i18n";
import { parseSrt } from "../utils/srt";

export interface SrtEntry {
  file: File;
  cueCount: number;
}

const sameFile = (a: File, b: File) => a.name === b.name && a.size === b.size && a.lastModified === b.lastModified;

export function useSrtFiles() {
  const entries = ref<SrtEntry[]>([]);
  const errors = ref<string[]>([]);
  const loading = ref(false);

  const totalCues = computed(() => entries.value.reduce((sum, e) => sum + e.cueCount, 0));

  /** Validates every candidate; valid ones are added, each invalid one yields an error message. */
  async function add(candidates: File[]) {
    errors.value = [];
    loading.value = true;
    try {
      const fresh = candidates.filter((c) => !entries.value.some((e) => sameFile(e.file, c)));
      const results = await Promise.allSettled(fresh.map((file) => parseSrt(file)));
      results.forEach((result, i) => {
        const { name } = fresh[i];
        if (result.status === "fulfilled") {
          entries.value.push({ file: fresh[i], cueCount: result.value.cueCount });
        } else {
          const reason = result.reason instanceof Error ? result.reason.message : t("translate.file.unreadable");
          errors.value.push(`${name}: ${reason}`);
        }
      });
    } finally {
      loading.value = false;
    }
  }

  function remove(file: File) {
    entries.value = entries.value.filter((e) => e.file !== file);
  }

  function keepOnly(files: File[]) {
    entries.value = entries.value.filter((e) => files.includes(e.file));
  }

  return { entries, errors, loading, totalCues, hasFiles: computed(() => entries.value.length > 0), add, remove, keepOnly };
}
