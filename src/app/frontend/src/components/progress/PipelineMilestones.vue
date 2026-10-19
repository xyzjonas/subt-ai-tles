<script setup lang="ts">
import type { MilestoneState } from "../../composables/useJobProgress";
import AppIcon from "../ui/AppIcon.vue";
import StatusBadge from "../ui/StatusBadge.vue";

defineProps<{ steps: { title: string; detail: string; state: MilestoneState }[] }>();

const LABEL: Record<MilestoneState, string> = { done: "Done", active: "Processing", pending: "Pending", skipped: "Skipped" };
</script>

<template>
  <section class="card" aria-labelledby="milestones-title">
    <header class="head">
      <h2 id="milestones-title">Progress</h2>
      <StatusBadge>{{ steps.length }} Steps</StatusBadge>
    </header>

    <ol class="steps">
      <li v-for="step in steps" :key="step.title" class="step" :class="step.state">
        <span class="marker">
          <AppIcon v-if="step.state === 'done'" name="check" :size="14" />
          <AppIcon v-else-if="step.state === 'active'" class="spin" name="sync" :size="14" />
        </span>
        <div class="text">
          <strong>{{ step.title }}</strong>
          <small class="mono">{{ step.detail }}</small>
        </div>
        <span class="state">{{ LABEL[step.state] }}</span>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.card {
  display: grid;
  gap: 12px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h2 {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.steps {
  display: grid;
  gap: 14px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
}

.marker {
  display: grid;
  place-items: center;
  flex: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--surface-subdued);
}

.done .marker {
  background: #d1fae5;
  color: #059669;
}

.active .marker {
  background: var(--primary-tint);
  color: var(--primary);
}

.text {
  display: grid;
  flex: 1;
  min-width: 0;
  gap: 2px;
}

strong {
  font-size: 14px;
  font-weight: 600;
}

.pending strong,
.skipped strong {
  color: var(--text-muted);
}

small {
  font-size: 11px;
  color: var(--text-muted);
}

.state {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}

.done .state {
  color: #059669;
}

.active .state {
  color: var(--primary);
}

.spin {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  to {
    rotate: 360deg;
  }
}

@media (prefers-reduced-motion: reduce) {
  .spin {
    animation: none;
  }
}
</style>
