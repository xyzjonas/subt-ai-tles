import { computed, onMounted, reactive, ref } from "vue";
import { getSettings, updateSettings } from "../api/settings";
import type { AppSettings } from "../api/types";
import { ApiError } from "../api/http";

export function useAdminSettings() {
  const saved = ref<AppSettings | null>(null);
  const draft = reactive({ model: "", temperature: 0 });
  const loading = ref(true);
  const saving = ref(false);
  const justSaved = ref(false);
  const error = ref("");

  function adopt(settings: AppSettings) {
    saved.value = settings;
    draft.model = settings.model;
    draft.temperature = settings.temperature;
  }

  onMounted(async () => {
    try {
      adopt(await getSettings());
    } catch {
      error.value = "Could not load the settings.";
    } finally {
      loading.value = false;
    }
  });

  const selected = computed(() => saved.value?.models.find((m) => m.id === draft.model));
  const dirty = computed(() => !!saved.value && (draft.model !== saved.value.model || draft.temperature !== saved.value.temperature));

  async function save() {
    saving.value = true;
    error.value = "";
    justSaved.value = false;
    try {
      adopt(await updateSettings({ model: draft.model, temperature: draft.temperature }));
      justSaved.value = true;
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : "Could not save the settings.";
    } finally {
      saving.value = false;
    }
  }

  function reset() {
    if (saved.value) adopt(saved.value);
    justSaved.value = false;
    error.value = "";
  }

  return { saved, draft, selected, dirty, loading, saving, justSaved, error, save, reset };
}
