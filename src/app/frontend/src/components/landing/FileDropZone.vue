<script setup lang="ts">
import { ref } from "vue";
import AppIcon from "../ui/AppIcon.vue";
import SelectedFileCard from "./SelectedFileCard.vue";

defineProps<{ file: File | null; cueCount: number; error: string; loading: boolean }>();
const emit = defineEmits<{ select: [file: File]; remove: [] }>();

const input = ref<HTMLInputElement | null>(null);
const dragging = ref(false);

function onPick(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files?.[0]) emit("select", target.files[0]);
  target.value = "";
}

function onDrop(event: DragEvent) {
  dragging.value = false;
  if (event.dataTransfer?.files[0]) emit("select", event.dataTransfer.files[0]);
}
</script>

<template>
  <section class="zone" aria-labelledby="source-label">
    <h2 id="source-label" class="section-label">Source subtitle file</h2>

    <SelectedFileCard v-if="file" :file="file" :cue-count="cueCount" @remove="$emit('remove')" />

    <div
      v-else
      class="drop"
      :class="{ dragging }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <span class="icon"><AppIcon name="upload" :size="24" /></span>
      <p class="cta">{{ loading ? "Reading file…" : "Tap to browse or drop .srt file" }}</p>
      <p class="hint">Accepts .srt, UTF-8 encoded up to 25MB</p>
      <button type="button" class="browse" @click="input?.click()">Select from device</button>
      <input ref="input" type="file" accept=".srt,text/plain,application/x-subrip" hidden @change="onPick" />
    </div>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
.zone {
  display: grid;
  gap: 10px;
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

.error {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--danger-bg);
  color: #b91c1c;
  font-size: 13px;
}
</style>
