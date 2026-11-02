<script setup lang="ts">
import type { Folder, Job } from "../../api/types";
import AppIcon from "../ui/AppIcon.vue";
import FolderMenu from "./FolderMenu.vue";

defineProps<{ job: Job; folders: Folder[]; folderName?: string }>();
const emit = defineEmits<{
  move: [folderId: string | null];
  createFolder: [name: string];
  archive: [];
  restore: [];
}>();
</script>

<template>
  <div class="actions">
    <FolderMenu :folders="folders" :current="job.folderId" :current-name="folderName" @select="emit('move', $event)" @create="emit('createFolder', $event)" />
    <button v-if="job.archivedAt" type="button" class="action" @click="emit('restore')">
      <AppIcon name="retry" :size="14" /> {{ $t("requests.archive.restore") }}
    </button>
    <button v-else-if="job.status !== 'processing'" type="button" class="action" @click="emit('archive')">
      <AppIcon name="archive" :size="14" /> {{ $t("requests.archive.action") }}
    </button>
  </div>
</template>

<style scoped>
.actions {
  /* above the card's stretched link */
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
}

.action:hover {
  background: var(--surface-subdued);
}
</style>
