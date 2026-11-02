<script setup lang="ts">
import { nextTick, ref } from "vue";
import type { Folder } from "../../api/types";
import { useJobDropTarget } from "../../composables/useJobDrag";
import AppIcon from "../ui/AppIcon.vue";

const props = defineProps<{ folder: Folder; count: number }>();
const emit = defineEmits<{ rename: [name: string]; remove: []; dropJob: [jobId: string] }>();

const { over, handlers } = useJobDropTarget((jobId) => emit("dropJob", jobId));

const renaming = ref(false);
const draft = ref("");
const input = ref<HTMLInputElement>();

async function startRename() {
  draft.value = props.folder.name;
  renaming.value = true;
  await nextTick();
  input.value?.select();
}

function commitRename() {
  if (!renaming.value) return;
  const name = draft.value.trim();
  renaming.value = false;
  if (name && name !== props.folder.name) emit("rename", name);
}
</script>

<template>
  <details class="folder" :class="{ over }" open v-on="handlers">
    <summary class="head">
      <AppIcon class="caret" name="chevron" :size="16" />
      <AppIcon name="folder" :size="18" />
      <form v-if="renaming" class="rename" @submit.prevent="commitRename" @click.prevent>
        <input ref="input" v-model="draft" type="text" maxlength="100" :aria-label="$t('requests.folder.renameLabel')" @blur="commitRename" @keydown.esc="renaming = false" />
      </form>
      <h2 v-else class="name">{{ folder.name }}</h2>
      <span class="count">{{ count }}</span>
      <span class="tools" @click.prevent>
        <button type="button" :aria-label="$t('requests.folder.rename')" :title="$t('requests.folder.rename')" @click="startRename">
          <AppIcon name="edit" :size="14" />
        </button>
        <button type="button" :aria-label="$t('requests.folder.delete')" :title="$t('requests.folder.delete')" @click="emit('remove')">
          <AppIcon name="trash" :size="14" />
        </button>
      </span>
    </summary>
    <div class="body">
      <slot />
      <p v-if="!count" class="hint">{{ $t("requests.folder.emptyHint") }}</p>
    </div>
  </details>
</template>

<style scoped>
.folder {
  border: 1px dashed transparent;
  border-radius: var(--radius-lg);
  background: var(--surface-subdued);
  transition: border-color 0.15s, background 0.15s;
}

.folder.over {
  border-color: var(--primary);
  background: var(--primary-tint);
}

.head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  color: var(--text-secondary);
  cursor: pointer;
  list-style: none;
}

.head::-webkit-details-marker {
  display: none;
}

.caret {
  transition: rotate 0.15s;
  rotate: -90deg;
}

.folder[open] .caret {
  rotate: 0deg;
}

.name {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rename {
  flex: 1;
  min-width: 0;
}

.rename input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid var(--primary);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.count {
  padding: 1px 8px;
  border-radius: var(--radius-tag);
  background: var(--surface);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.tools {
  display: flex;
  gap: 2px;
}

.tools button {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: var(--radius-sm);
  background: none;
  color: var(--text-muted);
  cursor: pointer;
}

.tools button:hover {
  background: var(--surface);
  color: var(--text);
}

.body {
  padding: 0 12px 12px;
}

.hint {
  padding: 8px 0;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
