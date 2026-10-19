<script setup lang="ts">
import { onMounted, ref } from "vue";
import { listJobs } from "../../api/jobs";
import type { Job } from "../../api/types";
import JobListItem from "./JobListItem.vue";

const jobs = ref<Job[]>([]);
onMounted(async () => {
  jobs.value = await listJobs(3);
});
</script>

<template>
  <section class="recent" aria-labelledby="recent-heading">
    <div class="head">
      <h2 id="recent-heading">Recent subtitle jobs</h2>
      <RouterLink to="/requests">View all</RouterLink>
    </div>
    <ul class="list">
      <li v-for="job in jobs" :key="job.id"><JobListItem :job="job" /></li>
    </ul>
  </section>
</template>

<style scoped>
.recent {
  display: grid;
  gap: 12px;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

h2 {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

a {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
}

.list {
  display: grid;
  grid-auto-rows: 1fr;
  gap: 8px;
}

.list li {
  display: grid;
}

@media (min-width: 768px) {
  .list {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}
</style>
