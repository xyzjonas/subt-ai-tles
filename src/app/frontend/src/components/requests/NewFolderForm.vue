<script setup lang="ts">
import { ref } from "vue";
import AppIcon from "../ui/AppIcon.vue";

const emit = defineEmits<{ create: [name: string] }>();
const name = ref("");

function submit() {
  const trimmed = name.value.trim();
  if (!trimmed) return;
  emit("create", trimmed);
  name.value = "";
}
</script>

<template>
  <form class="new" @submit.prevent="submit">
    <input v-model="name" type="text" maxlength="100" :placeholder="$t('requests.folder.newPlaceholder')" :aria-label="$t('requests.folder.newLabel')" />
    <button type="submit" :disabled="!name.trim()" :aria-label="$t('requests.folder.create')" :title="$t('requests.folder.create')">
      <AppIcon name="plus" :size="16" />
    </button>
  </form>
</template>

<style scoped>
.new {
  display: flex;
  gap: 6px;
}

input {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font: inherit;
  font-size: 13px;
  color: var(--text);
}

input:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

button {
  display: grid;
  place-items: center;
  width: 34px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: var(--primary-hover);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
