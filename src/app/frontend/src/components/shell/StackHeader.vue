<script setup lang="ts">
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ title: string; subtitle: string; backTo: string }>();
</script>

<template>
  <header class="header">
    <div class="bar">
      <RouterLink :to="backTo" class="back" :aria-label="$t('nav.back')"><AppIcon name="back" :size="18" /></RouterLink>
      <h1>
        <strong>{{ title }}</strong>
        <small>{{ subtitle }}</small>
      </h1>
      <button type="button" class="avatar" :aria-label="$t('nav.account')">
        <AppIcon name="user" :size="18" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  inset: 0 0 auto;
  z-index: 10;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.bar {
  max-width: var(--content-max);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--page-padding);
  display: flex;
  align-items: center;
  gap: 12px;
}

h1 {
  display: grid;
  margin-right: auto;
  line-height: 1.15;
}

strong {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

small {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
}

.back,
.avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--surface-subdued);
  color: var(--text-secondary);
}

.back:hover,
.avatar:hover {
  background: var(--border);
}
</style>
