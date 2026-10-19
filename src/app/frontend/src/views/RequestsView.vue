<script setup lang="ts">
import RequestCard from "../components/requests/RequestCard.vue";
import RequestSearch from "../components/requests/RequestSearch.vue";
import StatusTabs from "../components/requests/StatusTabs.vue";
import { useRequests } from "../composables/useRequests";

const { jobs, query, tab, loading, counts, visible } = useRequests();
</script>

<template>
  <section class="requests">
    <header class="head">
      <div class="title">
        <h1>Translation history</h1>
        <span class="count">● {{ jobs.length }} {{ jobs.length === 1 ? "task" : "tasks" }}</span>
      </div>
      <p>Review, track, and export active subtitle jobs.</p>
    </header>

    <RequestSearch v-model="query" />
    <StatusTabs v-model="tab" :counts="counts" />

    <p v-if="loading" class="empty" role="status">Loading…</p>
    <p v-else-if="!visible.length" class="empty">No {{ tab }} requests{{ query ? " match your search" : "" }}.</p>
    <ul v-else class="list">
      <li v-for="job in visible" :key="job.id"><RequestCard :job="job" /></li>
    </ul>
  </section>
</template>

<style scoped>
.requests {
  display: grid;
  gap: 16px;
}

.head {
  display: grid;
  gap: 4px;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.count {
  padding: 2px 10px;
  border-radius: var(--radius-tag);
  background: var(--primary-tint);
  color: var(--primary);
  font-size: 12px;
  font-weight: 600;
}

.head p {
  font-size: 13px;
  color: var(--text-secondary);
}

.list {
  display: grid;
  gap: 12px;
}

.empty {
  padding: 32px 0;
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
}

@media (min-width: 768px) {
  .list {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}
</style>
