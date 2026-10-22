<script setup lang="ts">
import type { Messages } from "../../i18n/en";
import PreviewIcon from "./PreviewIcon.vue";
import { fmt, plural } from "./previewData";

defineProps<{ t: Messages["preview"]["variants"]; locale: string; variants: string[]; current: string }>();
const emit = defineEmits<{ pick: [text: string] }>();
</script>

<template>
  <div class="picker">
    <p class="head">
      <span class="section-label"><PreviewIcon name="sparkle" :size="12" /> {{ t.title }}</span>
      <span class="hint">{{ t.hint }}</span>
    </p>

    <ul class="options">
      <li v-for="(text, i) in variants" :key="text">
        <button type="button" class="option" :class="{ active: text === current }" :aria-pressed="text === current" @click="emit('pick', text)">
          <span class="label">{{
            fmt(t.option, { n: i + 1, label: t.labels[i] ?? "", chars: plural(locale, t.chars, [...text].length) })
          }}</span>
          <span class="text" lang="cs">{{ text }}</span>
          <PreviewIcon v-if="text === current" class="tick" name="check" :size="16" />
        </button>
      </li>
    </ul>

    <form class="prompt" @submit.prevent>
      <input type="text" disabled :placeholder="t.placeholder" :aria-label="t.promptLabel" />
      <button type="submit" disabled><PreviewIcon name="play" :size="12" /> {{ t.run }}</button>
    </form>
  </div>
</template>

<style scoped>
.picker {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 10px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--primary);
}
.hint {
  font-size: 11px;
  color: var(--text-muted);
}
.options {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.option {
  position: relative;
  display: grid;
  gap: 2px;
  width: 100%;
  padding: 10px 36px 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font: inherit;
  text-align: left;
  color: inherit;
  cursor: pointer;
}
.option:hover {
  border-color: var(--primary);
}
.option.active {
  background: var(--primary-tint);
  border-color: var(--primary);
  color: #3730a3;
}
.label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}
.active .label {
  color: inherit;
}
.text {
  font-size: 14px;
  font-weight: 600;
}
.tick {
  position: absolute;
  right: 12px;
  top: 50%;
  translate: 0 -50%;
  color: var(--primary);
}
.prompt {
  display: flex;
  gap: 8px;
}
input {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  font: inherit;
  font-size: 13px;
}
.prompt button {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  font: inherit;
  font-weight: 600;
  color: #fff;
}
.prompt :disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
