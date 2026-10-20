<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from "vue";
import { useI18n } from "vue-i18n";
import type { CueVariant } from "../../api/types";
import { CPS_LIMIT, type EditorCue } from "../../composables/useCueEditor";
import { cps, formatTimecode, timeAgo } from "../../utils/srt";
import AppIcon from "../ui/AppIcon.vue";
import ErrorBanner from "../ui/ErrorBanner.vue";
import StatusBadge from "../ui/StatusBadge.vue";
import VariantPicker from "./VariantPicker.vue";

const props = defineProps<{
  cue: EditorCue;
  sourceLang?: string;
  targetLang: string;
  variants?: CueVariant[];
  status?: "loading" | "error";
  saving?: "saving" | "error";
  /** Localized reason shown when retranslating or saving failed. */
  problem?: string;
}>();

const { t, locale } = useI18n();
const emit = defineEmits<{
  retranslate: [prompt?: string];
  propose: [text: string];
  accept: [];
  discard: [];
  flag: [];
  dismiss: [];
}>();

/** What the target panel shows: the pending draft if there is one, else the stored text. */
const shown = computed(() => props.cue.draft ?? props.cue.target);
const pending = computed(() => props.cue.draft !== undefined);
const expanded = computed(() => !!props.variants || props.status === "loading");
const activeOption = computed(
  () =>
    (props.variants?.findIndex((v) => v.text === shown.value) ?? -1) + 1,
);
const duration = computed(() =>
  ((props.cue.end - props.cue.start) / 1000).toLocaleString(locale.value, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }),
);
const fast = computed(() => cps(props.cue) > CPS_LIMIT);
const index = computed(() => String(props.cue.index).padStart(3, "0"));

const editing = ref(false);
const draft = ref("");
const field = useTemplateRef("field");

async function edit() {
  draft.value = shown.value;
  editing.value = true;
  await nextTick();
  field.value?.focus();
}

function save() {
  if (!editing.value) return;
  editing.value = false;
  emit("propose", draft.value.trim());
}
</script>

<template>
  <article class="cue" :class="{ expanded }">
    <header class="head">
      <span class="index mono">#{{ index }}</span>
      <p class="time mono">
        <AppIcon name="play" :size="10" /> {{ formatTimecode(cue.start) }} →
        {{ formatTimecode(cue.end) }}
      </p>
      <StatusBadge v-if="expanded && activeOption" tone="primary"
        >{{ t("editor.cue.optionActive", { n: activeOption }) }}</StatusBadge
      >
      <StatusBadge v-else-if="cue.modifiedAt" tone="success"
        >{{ t("editor.cue.modified") }}</StatusBadge
      >
      <StatusBadge v-if="fast" tone="warning">{{ t("editor.cue.highCps") }}</StatusBadge>
      <span class="duration mono">{{ t("time.seconds", { n: duration }) }}</span>
    </header>

    <div class="texts">
      <section class="block">
        <h3 class="section-label">
          <span class="dot" /> {{ sourceLang ? t("editor.cue.source", { lang: sourceLang.toUpperCase() }) : t("editor.cue.sourceUnknown") }}
        </h3>
        <p class="source">{{ cue.source }}</p>
      </section>

      <section class="block target">
        <h3 class="section-label">
          <span class="dot target-dot" />
          {{ t("editor.cue.target", { lang: targetLang.toUpperCase() }) }}
          <span class="tag">{{
            pending ? t("editor.cue.unsaved") : cue.modifiedAt ? t("editor.cue.edited") : t("editor.cue.autoTuned")
          }}</span>
        </h3>
        <textarea
          v-if="editing"
          ref="field"
          v-model="draft"
          rows="2"
          :lang="targetLang"
          :aria-label="t('editor.cue.editLabel')"
          @blur="save"
          @keydown.esc.prevent="editing = false"
        />
        <p v-else class="translation" :lang="targetLang">{{ shown }}</p>
      </section>
    </div>

    <VariantPicker
      v-if="expanded"
      :variants="variants ?? []"
      :current="shown"
      :busy="status === 'loading'"
      @pick="emit('propose', $event)"
      @run="emit('retranslate', $event)"
    />
    <ErrorBanner
      v-if="status === 'error' || saving === 'error'"
      :title="t(status === 'error' ? 'editor.cue.alternativesFailed' : 'editor.cue.saveFailed')"
      :message="problem ?? t('errors.unknown')"
    />

    <footer class="foot">
      <button v-if="!expanded" type="button" @click="emit('retranslate')">
        <AppIcon name="retry" :size="14" /> {{ t("editor.cue.retranslate") }}
      </button>
      <button v-else type="button" @click="emit('dismiss')">
        <AppIcon name="close" :size="14" /> {{ t("editor.cue.close") }}
      </button>
      <button
        v-if="editing"
        type="button"
        class="done"
        @mousedown.prevent
        @click="save"
      >
        <AppIcon name="check" :size="14" /> {{ t("editor.cue.done") }}
      </button>
      <button v-else type="button" @click="edit">
        <AppIcon name="edit" :size="14" />
        {{ expanded ? t("editor.cue.manualEdit") : t("editor.cue.edit") }}
      </button>
      <button
        v-if="pending"
        type="button"
        class="accept"
        :disabled="saving === 'saving'"
        @click="emit('accept')"
      >
        <AppIcon name="check" :size="14" />
        {{ saving === "saving" ? t("editor.cue.saving") : t("editor.cue.accept") }}
      </button>
      <button
        v-if="pending"
        type="button"
        :disabled="saving === 'saving'"
        @click="emit('discard')"
      >
        <AppIcon name="close" :size="14" /> {{ t("editor.cue.discard") }}
      </button>
      <button
        type="button"
        class="flag"
        :class="{ on: cue.flagged }"
        :aria-pressed="cue.flagged"
        :aria-label="cue.flagged ? t('editor.cue.unflag') : t('editor.cue.flag')"
        @click="emit('flag')"
      >
        <AppIcon name="flag" :size="14" />
      </button>
      <span v-if="expanded && cue.modifiedAt" class="ago"
        >{{
          t("editor.cue.retranslated", { ago: timeAgo(new Date(cue.modifiedAt).toISOString()) })
        }}</span
      >
    </footer>
  </article>
</template>

<style scoped>
.cue {
  display: grid;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.cue.expanded {
  border: 2px solid var(--primary);
  padding: 13px 15px;
  box-shadow: 0 6px 20px var(--primary-glow);
}

.head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
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
  font-weight: 500;
}

.duration {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}

.texts {
  display: grid;
  gap: 10px;
}

.block {
  display: grid;
  gap: 4px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
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
  color: var(--primary);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0;
}

.source {
  font-size: 14px;
  color: #1e293b;
  white-space: pre-line;
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
  white-space: pre-line;
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
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
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
.foot .accept:hover:not(:disabled) {
  background: var(--primary-hover);
}

.foot button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.flag {
  width: 32px;
  padding: 0;
  justify-content: center;
}

.flag.on {
  background: var(--warning-bg);
  border-color: var(--warning);
  color: var(--warning-strong);
}

.ago {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}

@media (min-width: 768px) {
  .texts {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}
</style>
