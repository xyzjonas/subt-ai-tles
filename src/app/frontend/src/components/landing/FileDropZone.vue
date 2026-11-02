<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { MAX_SRT_MB } from "../../utils/srt";
import type { SrtEntry } from "../../composables/useSrtFiles";
import AppIcon from "../ui/AppIcon.vue";
import SelectedFileCard from "./SelectedFileCard.vue";

defineProps<{ entries: SrtEntry[]; errors: string[]; loading: boolean }>();
const emit = defineEmits<{ select: [files: File[]]; remove: [file: File] }>();

const { t } = useI18n();
const input = ref<HTMLInputElement | null>(null);
const dragging = ref(false);

function onPick(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files?.length) emit("select", Array.from(target.files));
  target.value = "";
}

function onDrop(event: DragEvent) {
  dragging.value = false;
  if (event.dataTransfer?.files.length) emit("select", Array.from(event.dataTransfer.files));
}
</script>

<template>
  <section class="zone" aria-labelledby="source-label">
    <h2 id="source-label" class="section-label">{{ t("translate.file.label") }}</h2>

    <ul v-if="entries.length" class="files">
      <li v-for="entry in entries" :key="`${entry.file.name}-${entry.file.size}-${entry.file.lastModified}`">
        <SelectedFileCard :file="entry.file" :cue-count="entry.cueCount" @remove="$emit('remove', entry.file)" />
      </li>
    </ul>

    <div
      class="drop"
      :class="{ dragging, compact: entries.length > 0 }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <span class="icon"><AppIcon name="upload" :size="24" /></span>
      <p class="cta">{{ loading ? t("translate.file.reading") : entries.length ? t("translate.file.promptMore") : t("translate.file.prompt") }}</p>
      <p class="hint">{{ t("translate.file.hint", { max: MAX_SRT_MB }) }}</p>
      <button type="button" class="browse" @click="input?.click()">{{ t("translate.file.browse") }}</button>
      <input ref="input" type="file" accept=".srt,text/plain,application/x-subrip" multiple hidden @change="onPick" />
    </div>

    <ul v-if="errors.length" class="errors" role="alert">
      <li v-for="message in errors" :key="message">{{ message }}</li>
    </ul>
  </section>
</template>

<style scoped>
.zone {
  display: grid;
  gap: 10px;
}

.files {
  display: grid;
  gap: 8px;
  list-style: none;
  padding: 0;
}

.drop.compact {
  padding: 16px 20px;
}

.drop.compact .icon,
.drop.compact .hint {
  display: none;
}

.drop {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 28px 20px;
  background: var(--surface);
  border: 1.5px dashed #cbd5e1;
  border-radius: var(--radius-lg);
  text-align: center;
  transition: border-color 0.15s, background 0.15s;
}

.drop.dragging {
  border-color: var(--primary);
  background: var(--primary-tint);
}

.icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  margin-bottom: 4px;
  border-radius: 50%;
  background: var(--primary-tint);
  color: var(--primary);
}

.cta {
  font-size: 15px;
  font-weight: 600;
}

.hint {
  font-size: 12px;
  color: var(--text-muted);
}

.browse {
  height: 40px;
  margin-top: 8px;
  padding: 0 18px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--primary-tint);
  color: var(--primary);
  font-weight: 600;
}

.browse:hover {
  background: #ddd6fe;
}

.errors {
  display: grid;
  gap: 4px;
  list-style: none;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--danger-bg);
  overflow-wrap: anywhere;
  color: #b91c1c;
  font-size: 13px;
}
</style>
