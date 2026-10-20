<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { CueVariant } from "../../api/types";
import AppIcon from "../ui/AppIcon.vue";

defineProps<{ variants: CueVariant[]; current: string; busy: boolean }>();
const emit = defineEmits<{ pick: [text: string]; run: [prompt: string] }>();

const { t } = useI18n();
const prompt = ref("");

function run() {
  const text = prompt.value.trim();
  if (!text) return;
  emit("run", text);
  prompt.value = "";
}
</script>

<template>
  <div class="picker">
    <p class="head">
      <span class="section-label"><AppIcon name="sparkle" :size="12" /> {{ t("editor.variants.title") }}</span>
      <span class="hint">{{ t("editor.variants.hint") }}</span>
    </p>

    <ul class="options">
      <li v-for="(v, i) in variants" :key="`${v.label}-${i}`">
        <button type="button" class="option" :class="{ active: v.text === current }" :aria-pressed="v.text === current" @click="emit('pick', v.text)">
          <span class="label">{{ t("editor.variants.option", { n: i + 1, label: v.label, chars: t("editor.variants.chars", { count: [...v.text].length }, [...v.text].length) }) }}</span>
          <span class="text">{{ v.text }}</span>
          <AppIcon v-if="v.text === current" class="tick" name="check" :size="16" />
        </button>
      </li>
    </ul>

    <form class="prompt" @submit.prevent="run">
      <input v-model="prompt" type="text" :placeholder="t('editor.variants.placeholder')" :aria-label="t('editor.variants.promptLabel')" :disabled="busy" />
      <button type="submit" :disabled="busy || !prompt.trim()"><AppIcon name="play" :size="12" /> {{ busy ? t("editor.variants.running") : t("editor.variants.run") }}</button>
    </form>
  </div>
</template>

<style scoped>
.picker {
  display: grid;
  gap: 10px;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary);
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
}

.options {
  display: grid;
  gap: 8px;
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
  text-align: left;
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
  color: var(--text);
}

input:focus {
  outline: 2px solid var(--primary);
  outline-offset: 0;
}

.prompt button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: #fff;
  font-weight: 600;
}

.prompt button:hover:not(:disabled) {
  background: var(--primary-hover);
}

.prompt button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
