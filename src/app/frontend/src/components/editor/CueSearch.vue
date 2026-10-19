<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef } from "vue";
import AppIcon from "../ui/AppIcon.vue";

const model = defineModel<string>({ required: true });
const input = useTemplateRef("input");

function onKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    input.value?.focus();
  }
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onUnmounted(() => window.removeEventListener("keydown", onKeydown));
</script>

<template>
  <label class="search">
    <AppIcon name="search" :size="18" />
    <input ref="input" v-model="model" type="search" placeholder="Search line text or #cue number..." aria-label="Search cues" />
    <kbd class="mono">⌘K</kbd>
  </label>
</template>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-placeholder);
}

.search:focus-within {
  outline: 2px solid var(--primary);
}

input {
  flex: 1;
  min-width: 0;
  padding: 10px 0;
  border: 0;
  outline: 0;
  background: none;
  font: inherit;
  font-size: 14px;
  color: var(--text);
}

kbd {
  padding: 2px 6px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface-subdued);
  font-size: 11px;
  color: var(--text-muted);
}

@media (hover: none) {
  kbd {
    display: none;
  }
}
</style>
