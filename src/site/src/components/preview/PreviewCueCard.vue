<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from "vue";
import type { Messages } from "../../i18n/en";
import PreviewBadge from "./PreviewBadge.vue";
import PreviewIcon from "./PreviewIcon.vue";
import PreviewVariants from "./PreviewVariants.vue";
import { CPS_LIMIT, cps, formatTimecode, fmt, type PreviewCue } from "./previewData";

const props = defineProps<{ cue: PreviewCue; t: Messages["preview"]; locale: string }>();

const target = ref(props.cue.target);
/** Pending, not yet accepted text (a picked variant or a manual edit). */
const draft = ref<string>();
const modified = ref(false);
const expanded = ref(props.cue.expanded ?? false);
const flagged = ref(false);

const shown = computed(() => draft.value ?? target.value);
const pending = computed(() => draft.value !== undefined);
const variants = computed(() => props.cue.variants ?? []);
const activeOption = computed(() => variants.value.indexOf(shown.value) + 1);
const fast = computed(() => cps(target.value, props.cue.start, props.cue.end) > CPS_LIMIT);
const duration = computed(() =>
  ((props.cue.end - props.cue.start) / 1000).toLocaleString(props.locale, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }),
);

const editing = ref(false);
const editText = ref("");
const field = useTemplateRef("field");

async function edit() {
  editText.value = shown.value;
  editing.value = true;
  await nextTick();
  field.value?.focus();
}

function propose(text: string) {
  draft.value = text === target.value ? undefined : text;
}

function save() {
  if (!editing.value) return;
  editing.value = false;
  if (editText.value.trim()) propose(editText.value.trim());
}

function accept() {
  if (draft.value === undefined) return;
  target.value = draft.value;
  draft.value = undefined;
  modified.value = true;
}
</script>

<template>
  <article class="cue" :class="{ expanded }">
    <header class="head">
      <span class="index mono">#{{ cue.index }}</span>
      <p class="time mono">
        <PreviewIcon name="play" :size="10" /> {{ formatTimecode(cue.start) }} → {{ formatTimecode(cue.end) }}
      </p>
      <PreviewBadge v-if="expanded && activeOption" tone="primary">{{ fmt(t.cue.optionActive, { n: activeOption }) }}</PreviewBadge>
      <PreviewBadge v-else-if="modified" tone="success">{{ t.cue.modified }}</PreviewBadge>
      <PreviewBadge v-if="fast" tone="warning">{{ t.cue.highCps }}</PreviewBadge>
      <span class="duration mono">{{ fmt(t.cue.seconds, { n: duration }) }}</span>
    </header>

    <div class="texts">
      <section class="block">
        <h3 class="section-label"><span class="dot" /> {{ t.cue.source }}</h3>
        <p class="source" lang="en">{{ cue.source }}</p>
      </section>

      <section class="block target">
        <h3 class="section-label">
          <span class="dot target-dot" /> {{ t.cue.target }}
          <span class="tag">{{ pending ? t.cue.unsaved : modified ? t.cue.edited : t.cue.autoTuned }}</span>
        </h3>
        <textarea v-if="editing" ref="field" v-model="editText" rows="2" lang="cs" :aria-label="t.cue.editLabel" @blur="save" @keydown.esc.prevent="editing = false" />
        <p v-else class="translation" lang="cs">{{ shown }}</p>
      </section>
    </div>

    <PreviewVariants v-if="expanded" :t="t.variants" :locale="locale" :variants="variants" :current="shown" @pick="propose" />

    <footer class="foot">
      <button v-if="!expanded" type="button" @click="expanded = true">
        <PreviewIcon name="retry" :size="14" /> {{ t.cue.retranslate }}
      </button>
      <button v-else type="button" @click="expanded = false">
        <PreviewIcon name="close" :size="14" /> {{ t.cue.close }}
      </button>
      <button v-if="editing" type="button" class="done" @mousedown.prevent @click="save">
        <PreviewIcon name="check" :size="14" /> {{ t.cue.done }}
      </button>
      <button v-else type="button" @click="edit">
        <PreviewIcon name="edit" :size="14" /> {{ expanded ? t.cue.manualEdit : t.cue.edit }}
      </button>
      <button v-if="pending" type="button" class="accept" @click="accept">
        <PreviewIcon name="check" :size="14" /> {{ t.cue.accept }}
      </button>
      <button v-if="pending" type="button" @click="draft = undefined">
        <PreviewIcon name="close" :size="14" /> {{ t.cue.discard }}
      </button>
      <button type="button" class="flag" :class="{ on: flagged }" :aria-pressed="flagged" :aria-label="flagged ? t.cue.unflag : t.cue.flag" @click="flagged = !flagged">
        <PreviewIcon name="flag" :size="14" />
      </button>
      <span v-if="expanded && modified" class="ago">{{ fmt(t.cue.retranslated, { ago: t.cue.justNow }) }}</span>
    </footer>
  </article>
</template>

<style scoped>
.cue {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.cue.expanded {
  border: 2px solid var(--primary);
  padding: 13px 15px;
  box-shadow: 0 6px 20px var(--primary-glow-soft);
}
.head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.mono {
  font-family: var(--font-mono);
  font-weight: 500;
}
.index {
  padding: 2px 8px;
  border-radius: 6px;
  background: #e0e7ff;
  color: #4338ca;
  font-size: 12px;
}
.time {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.duration {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}
.texts {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 10px;
}
.block {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 4px;
}
.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-placeholder);
}
.target-dot {
  background: var(--primary);
}
.tag {
  margin-left: auto;
  padding: 1px 8px;
  border-radius: var(--radius-tag);
  background: var(--primary-tint);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0;
  color: var(--primary);
}
.source {
  font-size: 14px;
  color: #1e293b;
}
.target {
  padding: 10px 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}
.translation,
textarea {
  font: inherit;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}
textarea {
  width: 100%;
  padding: 0;
  border: 0;
  outline: 0;
  resize: none;
  field-sizing: content;
  background: none;
  color: var(--text);
}
.target:focus-within {
  outline: 2px solid var(--primary);
}
.foot {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.foot button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
}
.foot button:hover {
  background: var(--border);
}
.foot .done,
.foot .accept {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.foot .done:hover,
.foot .accept:hover {
  background: var(--primary-hover);
}
.foot .flag {
  width: 32px;
  padding: 0;
  justify-content: center;
}
.foot .flag.on {
  background: var(--warning-bg);
  border-color: var(--warning);
  color: var(--warning-strong);
}
.ago {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}
@container (min-width: 600px) {
  .texts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: start;
  }
}
</style>
