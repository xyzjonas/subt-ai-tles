<script setup lang="ts">
import { onMounted, ref } from "vue";

const message = ref("loading...");

onMounted(async () => {
  const res = await fetch("/api/hello");
  message.value = (await res.json()).message;
});
</script>

<template>
  <main>
    <h1>subt-ai-tles</h1>
    <p>{{ message }}</p>
  </main>
</template>
