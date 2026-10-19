<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import JobControls from "../components/progress/JobControls.vue";
import JobOverview from "../components/progress/JobOverview.vue";
import LiveCueStream from "../components/progress/LiveCueStream.vue";
import PipelineMilestones from "../components/progress/PipelineMilestones.vue";
import ProgressGauge from "../components/progress/ProgressGauge.vue";
import { useJobProgress } from "../composables/useJobProgress";

const route = useRoute();
const router = useRouter();
const id = computed(() => String(route.params.id));

// Finished jobs open the editor; a cancelled job has nothing left to show.
let cancelled = false;
const { job, cue, error, cancelling, processed, total, percent, chunkPercent, milestones, retry, cancel } = useJobProgress(id, () =>
  router.replace(cancelled ? "/requests" : { name: "editor", params: { id: id.value } }),
);

function confirmCancel() {
  if (!confirm("Cancel this translation? Tokens already consumed are still billed.")) return;
  cancelled = true;
  cancel();
}
</script>

<template>
  <p v-if="error" class="state" role="alert">{{ error }} <button type="button" @click="retry">Retry</button></p>
  <p v-else-if="!job" class="state" role="status">Loading…</p>

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

.state button {
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  font-weight: 600;
  color: var(--text-secondary);
}
</style>
