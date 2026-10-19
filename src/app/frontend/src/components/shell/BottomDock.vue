<script setup lang="ts">
import AppIcon from "../ui/AppIcon.vue";
</script>

<template>
  <nav class="dock" aria-label="Primary">
    <RouterLink to="/" class="tab">
      <AppIcon name="translate" />
      Translate
    </RouterLink>
    <RouterLink to="/requests" class="tab">
      <AppIcon name="list" />
      My requests
    </RouterLink>
    <RouterLink to="/dashboard" class="tab">
      <AppIcon name="user" />
      Dashboard
    </RouterLink>
  </nav>
</template>

<style scoped>
.dock {
  position: fixed;
  inset: auto 0 0;
  z-index: 10;
  height: var(--dock-height);
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--surface);
  border-top: 1px solid var(--border);
}

@media (min-width: 768px) {
  .dock {
    display: none;
  }
}

.tab {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-placeholder);
}

.tab.router-link-exact-active {
  color: var(--primary);
}

.tab.router-link-exact-active::before {
  content: "";
  position: absolute;
  top: -1px;
  width: 32px;
  height: 3px;
  border-radius: 0 0 3px 3px;
  background: var(--primary);
}
</style>
