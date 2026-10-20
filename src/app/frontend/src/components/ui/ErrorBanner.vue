<script setup lang="ts">
import AppIcon from "./AppIcon.vue";

defineProps<{ title: string; message: string }>();
</script>

<template>
  <div class="banner" role="alert">
    <AppIcon name="alert" :size="20" />
    <div>
      <strong>{{ title }}</strong>
      <p>{{ message }}</p>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--danger);
  border-left-width: 4px;
  border-radius: var(--radius-md);
  background: var(--danger-bg);
  color: #991b1b;
}

.banner > svg {
  flex: none;
  margin-top: 1px;
  color: var(--danger);
}

strong {
  font-size: 14px;
  font-weight: 700;
}

p {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.5;
}
</style>
