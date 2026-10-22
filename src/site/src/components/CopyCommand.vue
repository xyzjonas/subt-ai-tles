<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";

const props = defineProps<{
  lines: string[];
  label: string;
  copyText: string;
  copiedText: string;
}>();

const copied = ref(false);
let timer: ReturnType<typeof setTimeout> | undefined;

const text = computed(() => props.lines.join("\n"));

async function copy() {
  try {
    await navigator.clipboard.writeText(text.value);
  } catch {
    return;
  }
  copied.value = true;
  clearTimeout(timer);
  timer = setTimeout(() => (copied.value = false), 1800);
}

onBeforeUnmount(() => clearTimeout(timer));
</script>

<template>
  <div class="terminal">
    <header>
      <span class="dots" aria-hidden="true"><i /><i /><i /></span>
      <span class="label">{{ label }}</span>
      <button type="button" @click="copy">
        <span aria-live="polite">{{ copied ? copiedText : `📋 ${copyText}` }}</span>
      </button>
    </header>
    <pre><code><template v-for="line in lines" :key="line"><span class="prompt">$ </span>{{ line }}
</template></code></pre>
  </div>
</template>

<style scoped>
.terminal {
  max-width: 48rem;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 12px;
  background: var(--terminal);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2);
  color: #f1f5f9;
  font-family: var(--font-mono);
}
header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid #1e293b;
}
.dots {
  display: flex;
  gap: 6px;
}
.dots i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dots i:nth-child(1) { background: #f87171; }
.dots i:nth-child(2) { background: #fbbf24; }
.dots i:nth-child(3) { background: #4ade80; }
.label {
  flex: 1;
  font-size: 12px;
  color: #94a3b8;
}
button {
  padding: 4px 10px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #1e293b;
  font: inherit;
  font-size: 12px;
  color: #e2e8f0;
  cursor: pointer;
}
button:hover {
  background: #334155;
}
pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.7;
}
.prompt {
  color: #818cf8;
  user-select: none;
}
</style>
