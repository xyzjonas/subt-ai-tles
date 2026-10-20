<script setup lang="ts">
import { useI18n } from "vue-i18n";
import type { CueFilter } from "../../composables/useCueEditor";
import PillOption from "../ui/PillOption.vue";

const model = defineModel<CueFilter>({ required: true });
defineProps<{ counts: Record<CueFilter, number> }>();

const { t, n } = useI18n();
const TABS: CueFilter[] = ["all", "modified", "flagged", "cps"];
</script>

<template>
  <div class="filters" role="group" :aria-label="t('editor.filters.label')">
    <PillOption v-for="tab in TABS" :key="tab" :active="model === tab" @click="model = tab">
      {{ t("editor.filters.item", { label: t(`editor.filters.${tab}`), count: n(counts[tab]) }) }}
    </PillOption>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}
</style>
