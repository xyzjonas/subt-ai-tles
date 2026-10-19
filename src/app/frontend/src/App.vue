<script setup lang="ts">
import { useRoute } from "vue-router";
import AppHeader from "./components/shell/AppHeader.vue";
import BottomDock from "./components/shell/BottomDock.vue";

const route = useRoute();
</script>

<template>
  <div class="shell">
    <AppHeader :subtitle="String(route.meta.subtitle ?? '')" />
    <main class="content">
      <RouterView />
    </main>
    <BottomDock />
  </div>
</template>

<style scoped>
.shell {
  min-height: 100dvh;
}

.content {
  max-width: var(--content-max);
  margin: 0 auto;
  padding: calc(var(--header-height) + 20px) var(--page-padding) calc(var(--dock-height) + 32px);
}

@media (min-width: 768px) {
  .content {
    padding-top: calc(var(--header-height) + 32px);
    padding-bottom: 48px;
  }
}
</style>
