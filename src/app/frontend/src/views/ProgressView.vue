<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import ErrorBanner from "../components/ui/ErrorBanner.vue";
import JobControls from "../components/progress/JobControls.vue";
import JobOverview from "../components/progress/JobOverview.vue";
import LiveCueStream from "../components/progress/LiveCueStream.vue";
import PipelineMilestones from "../components/progress/PipelineMilestones.vue";
import ProgressGauge from "../components/progress/ProgressGauge.vue";
import { useJobProgress } from "../composables/useJobProgress";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const id = computed(() => String(route.params.id));

// Finished jobs open the editor; a cancelled job has nothing left to show.
let cancelled = false;
const { job, cue, error, cancelling, processed, total, percent, chunkPercent, milestones, retry, cancel } = useJobProgress(id, () =>
  router.replace(cancelled ? "/requests" : { name: "editor", params: { id: id.value } }),
);

function confirmCancel() {
  if (!confirm(t("progress.confirmCancel"))) return;
  cancelled = true;
  cancel();
}
</script>

<template>
  <ErrorBanner v-if="error" :title="t('errors.title')" :message="error">
    <button type="button" class="retry" @click="retry">{{ t("retry") }}</button>
  </ErrorBanner>
  <p v-else-if="!job" class="state" role="status">{{ t("loading") }}</p>

  <section v-else class="progress">
    <JobOverview :job="job" />
    <ProgressGauge :percent="percent" :processed="processed" :total="total" :chunk-percent="chunkPercent" />
    <PipelineMilestones :steps="milestones" />
    <LiveCueStream :cue="cue" />
    <JobControls :cancelling="cancelling" @cancel="confirmCancel" />
  </section>
</template>

<style scoped>
.progress {
  display: grid;
  gap: 16px;
}

.state {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}

.retry {
  height: 36px;
  margin-top: 10px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  font-weight: 600;
  color: var(--text-secondary);
}
</style>
