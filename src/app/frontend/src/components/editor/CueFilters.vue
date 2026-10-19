<script setup lang="ts">
import type { CueFilter } from "../../composables/useCueEditor";
import PillOption from "../ui/PillOption.vue";

const model = defineModel<CueFilter>({ required: true });
defineProps<{ counts: Record<CueFilter, number> }>();

const TABS: { value: CueFilter; label: string }[] = [
  { value: "all", label: "All lines" },
  { value: "modified", label: "Modified" },
  { value: "flagged", label: "Flagged" },
  { value: "cps", label: "High CPS" },
];
</script>

<template>
  <div class="filters" role="group" aria-label="Filter cues">
    <PillOption v-for="t in TABS" :key="t.value" :active="model === t.value" @click="model = t.value">
      {{ t.label }} ({{ counts[t.value].toLocaleString() }})
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
