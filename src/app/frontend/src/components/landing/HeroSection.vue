<script setup lang="ts">
import StatusBadge from "../ui/StatusBadge.vue";
</script>

<template>
  <section class="hero">
    <StatusBadge tone="primary">✦ Contextual Neural Engine</StatusBadge>
    <h1>Translate subtitles with AI</h1>
    <p>Upload any .srt file, pick your languages, and let LLMs deliver contextual, synchronized translations.</p>
  </section>
</template>

<style scoped>
.hero {
  display: grid;
  justify-items: start;
  gap: 10px;
}

h1 {
  font-size: 24px;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: -0.02em;
}

p {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
