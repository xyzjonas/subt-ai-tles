<script setup lang="ts">
import { computed } from "vue";
import type { RequestTab } from "../../composables/useRequests";
import SegmentedTabs from "../ui/SegmentedTabs.vue";

const model = defineModel<RequestTab>({ required: true });
const props = defineProps<{ counts: Record<RequestTab, number> }>();

const tabs = computed(() => [
  { value: "processing" as const, label: `Processing (${props.counts.processing})` },
  { value: "completed" as const, label: `Completed (${props.counts.completed})` },
]);
</script>

<template>
  <SegmentedTabs v-model="model" :tabs="tabs" label="Request status" />
</template>
