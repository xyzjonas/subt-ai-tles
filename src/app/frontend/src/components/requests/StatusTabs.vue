<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { RequestTab } from "../../composables/useRequests";
import SegmentedTabs from "../ui/SegmentedTabs.vue";

const model = defineModel<RequestTab>({ required: true });
const props = defineProps<{ counts: Record<RequestTab, number> }>();
const { t } = useI18n();

const tabs = computed(() => [
  { value: "processing" as const, label: t("requests.tabs.processing", { count: props.counts.processing }) },
  { value: "completed" as const, label: t("requests.tabs.completed", { count: props.counts.completed }) },
]);
</script>

<template>
  <SegmentedTabs v-model="model" :tabs="tabs" :label="t('requests.tabs.label')" />
</template>
