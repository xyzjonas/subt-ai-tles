<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppHeader from "./components/shell/AppHeader.vue";
import BottomDock from "./components/shell/BottomDock.vue";
import StackHeader from "./components/shell/StackHeader.vue";

const route = useRoute();
const stack = computed(() => route.meta.layout === "stack");
</script>

<template>
  <div class="shell">
    <StackHeader v-if="stack" :title="String(route.meta.title)" :subtitle="String(route.meta.subtitle)" back-to="/requests" />
    <AppHeader v-else :subtitle="String(route.meta.subtitle ?? '')" />
    <main class="content" :class="{ stack }">
      <RouterView />
    </main>
    <BottomDock v-if="!stack" />
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

.content.stack {
  padding-bottom: calc(var(--action-bar-height) + 32px);
}
</style>
