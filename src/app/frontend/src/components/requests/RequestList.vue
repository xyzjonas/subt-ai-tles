<script setup lang="ts">
import type { Folder, Job } from "../../api/types";
import RequestCard from "./RequestCard.vue";

defineProps<{ jobs: Job[]; folders: Folder[]; folderName: (id?: string) => string | undefined }>();
defineEmits<{
  move: [jobId: string, folderId: string | null];
  createFolder: [jobId: string, name: string];
  archive: [jobId: string];
  restore: [jobId: string];
}>();
</script>

<template>
  <ul class="list">
    <li v-for="job in jobs" :key="job.id">
      <RequestCard
        :job="job"
        :folders="folders"
        :folder-name="folderName(job.folderId)"
        @move="$emit('move', job.id, $event)"
        @create-folder="$emit('createFolder', job.id, $event)"
        @archive="$emit('archive', job.id)"
        @restore="$emit('restore', job.id)"
      />
    </li>
  </ul>
</template>

<style scoped>
.list {
  display: grid;
  gap: 12px;
}

@media (min-width: 768px) {
  .list {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}
</style>
