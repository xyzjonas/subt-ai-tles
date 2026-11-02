<script setup lang="ts">
import { ref } from "vue";
import type { Folder } from "../../api/types";
import AppIcon from "../ui/AppIcon.vue";
import NewFolderForm from "./NewFolderForm.vue";

defineProps<{ folders: Folder[]; current?: string; currentName?: string }>();
const emit = defineEmits<{ select: [folderId: string | null]; create: [name: string] }>();

const menu = ref<HTMLDetailsElement>();

function choose(folderId: string | null) {
  menu.value?.removeAttribute("open");
  emit("select", folderId);
}

function create(name: string) {
  menu.value?.removeAttribute("open");
  emit("create", name);
}
</script>

<template>
  <details ref="menu" class="menu">
    <summary class="trigger">
      <AppIcon name="folder" :size="14" />
      {{ currentName ?? $t("requests.folder.add") }}
    </summary>
    <div class="panel">
      <p class="heading">{{ $t("requests.folder.moveTo") }}</p>
      <ul class="options">
        <li v-if="current">
          <button type="button" @click="choose(null)">{{ $t("requests.folder.remove") }}</button>
        </li>
        <li v-for="folder in folders" :key="folder.id">
          <button type="button" :aria-current="folder.id === current" @click="choose(folder.id)">
            <AppIcon name="folder" :size="14" /> {{ folder.name }}
            <AppIcon v-if="folder.id === current" class="tick" name="check" :size="14" />
          </button>
        </li>
      </ul>
      <NewFolderForm @create="create" />
    </div>
  </details>
</template>

<style scoped>
.menu {
  position: relative;
}

.trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 180px;
  padding: 7px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  list-style: none;
}

.trigger::-webkit-details-marker {
  display: none;
}

.trigger:hover,
.menu[open] .trigger {
  background: var(--surface-subdued);
}

.panel {
  position: absolute;
  z-index: 10;
  bottom: calc(100% + 6px);
  left: 0;
  display: grid;
  gap: 8px;
  width: 240px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}

.heading {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
}

.options {
  display: grid;
  gap: 2px;
  max-height: 180px;
  overflow-y: auto;
}

.options button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 8px;
  border: 0;
  border-radius: var(--radius-sm);
  background: none;
  font: inherit;
  font-size: 13px;
  text-align: left;
  color: var(--text);
  cursor: pointer;
}

.options button:hover {
  background: var(--surface-subdued);
}

.options button[aria-current="true"] {
  color: var(--primary);
  font-weight: 600;
}

.tick {
  margin-left: auto;
}
</style>
