<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import CueCard from "../components/editor/CueCard.vue";
import CueFilters from "../components/editor/CueFilters.vue";
import CueSearch from "../components/editor/CueSearch.vue";
import EditorActionBar from "../components/editor/EditorActionBar.vue";
import EditorSummary from "../components/editor/EditorSummary.vue";
import AppIcon from "../components/ui/AppIcon.vue";
import { useCueEditor } from "../composables/useCueEditor";
import { compileSrt, downloadBlob, srtBlob, translatedFileName } from "../utils/srt";

const route = useRoute();
const { job, cues, loading, error, query, filter, counts, visible, remaining, runningTime, variants, status, saving, pending, load, propose, accept, discard, retranslate, dismiss, toggleFlag, showMore } =
  useCueEditor(computed(() => String(route.params.id)));

const canShare = "share" in navigator;
const copied = ref(false);

function download() {
  if (job.value) downloadBlob(srtBlob(cues.value), translatedFileName(job.value));
}

async function copy() {
  await navigator.clipboard.writeText(compileSrt(cues.value));
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}

function share() {
  if (!job.value) return;
  const file = new File([srtBlob(cues.value)], translatedFileName(job.value), { type: "application/x-subrip" });
  navigator.share(navigator.canShare?.({ files: [file] }) ? { files: [file] } : { title: job.value.fileName, text: compileSrt(cues.value) }).catch(() => {});
}

function sync() {
  if (pending.value && !confirm("Re-syncing reloads all lines and discards changes you haven't accepted. Continue?")) return;
  load();
}
</script>

<template>
  <p v-if="loading && !job" class="state" role="status">Loading…</p>
  <p v-else-if="error" class="state" role="alert">{{ error }} <button type="button" @click="load">Retry</button></p>

  <section v-else-if="job" class="editor">
    <RouterLink to="/requests" class="back"><AppIcon name="back" :size="14" /> Back to My Requests</RouterLink>

    <EditorSummary :job="job" :lines="cues.length" :running-time="runningTime" :copied="copied" :can-share="canShare" @download="download" @copy="copy" @share="share" />

    <CueSearch v-model="query" />
    <CueFilters v-model="filter" :counts="counts" />

    <p v-if="!visible.length" class="state">No lines match.</p>
    <ul v-else class="cues">
      <li v-for="cue in visible" :key="cue.index">
        <CueCard
          :cue="cue"
          :source-lang="job.sourceLang"
          :target-lang="job.targetLang"
          :variants="variants[cue.index]"
          :status="status[cue.index]"
          :saving="saving[cue.index]"
          @retranslate="retranslate(cue, $event)"
          @propose="propose(cue, $event)"
          @accept="accept(cue)"
          @discard="discard(cue)"
          @flag="toggleFlag(cue)"
          @dismiss="dismiss(cue)"
        />
      </li>
    </ul>
    <button v-if="remaining > 0" type="button" class="more" @click="showMore">Show more ({{ remaining.toLocaleString() }} left)</button>

    <EditorActionBar :syncing="loading" @download="download" @sync="sync" />
  </section>
</template>

<style scoped>
.editor {
  display: grid;
  gap: 16px;
}

.back {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--primary);
}

.cues {
  display: grid;
  gap: 12px;
}

.state {
  padding: 32px 0;
  text-align: center;
  color: var(--text-muted);
}

.state button,
.more {
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-subdued);
  font-weight: 600;
  color: var(--text-secondary);
}

.more {
  justify-self: center;
}
</style>
