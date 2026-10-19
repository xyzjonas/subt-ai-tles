<script setup lang="ts">
import AppIcon from "../ui/AppIcon.vue";

const model = defineModel<string>({ required: true });
</script>

<template>
  <label class="search">
    <AppIcon name="search" :size="18" />
    <input v-model="model" type="search" placeholder="Search files or languages..." aria-label="Search requests" />
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
</style>
