<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import FolderGroup from "../components/requests/FolderGroup.vue";
import NewFolderForm from "../components/requests/NewFolderForm.vue";
import RequestList from "../components/requests/RequestList.vue";
import RequestSearch from "../components/requests/RequestSearch.vue";
import StatusTabs from "../components/requests/StatusTabs.vue";
import ErrorBanner from "../components/ui/ErrorBanner.vue";
import { useJobDropTarget } from "../composables/useJobDrag";
import { useRequests } from "../composables/useRequests";

const { t } = useI18n();
const { active, folders, query, tab, loading, error, counts, sections, ungrouped, folderName, moveToFolder, archive, restore, addFolder, addFolderAndMove, rename, removeFolder } =
  useRequests();

const inArchive = computed(() => tab.value === "archived");
const empty = computed(() => !sections.value.length && !ungrouped.value.length);
// only worth labelling the loose requests when there are folders to tell them apart from
const labelUngrouped = computed(() => sections.value.length > 0 && ungrouped.value.length > 0);

const ungroupedDrop = useJobDropTarget((jobId) => moveToFolder(jobId, null));
</script>

<template>
  <section class="requests">
    <header class="head">
      <div class="title">
        <h1>{{ t("requests.title") }}</h1>
        <span class="count">● {{ t("requests.tasks", { count: active.length }, active.length) }}</span>
      </div>
      <p>{{ inArchive ? t("requests.archive.lead") : t("requests.lead") }}</p>
    </header>

    <RequestSearch v-model="query" />
    <StatusTabs v-model="tab" :counts="counts" />
    <NewFolderForm v-if="!inArchive" @create="addFolder" />

    <ErrorBanner v-if="error" :title="t('errors.title')" :message="error" />

    <p v-if="loading" class="empty" role="status">{{ t("loading") }}</p>
    <template v-else>
      <p v-if="empty" class="empty">{{ t(`requests.empty.${tab}${query ? "Search" : ""}`) }}</p>

      <FolderGroup v-for="s in sections" :key="s.folder.id" :folder="s.folder" :count="s.jobs.length" @rename="rename(s.folder, $event)" @remove="removeFolder(s.folder)" @drop-job="moveToFolder($event, s.folder.id)">
        <RequestList :jobs="s.jobs" :folders="folders" :folder-name="folderName" @move="moveToFolder" @create-folder="(id, name) => addFolderAndMove(name, id)" @archive="archive" @restore="restore" />
      </FolderGroup>

      <div v-if="ungrouped.length || sections.length" class="loose" :class="{ over: ungroupedDrop.over.value }" v-on="ungroupedDrop.handlers">
        <h2 v-if="labelUngrouped" class="label">{{ t("requests.folder.ungrouped") }}</h2>
        <RequestList :jobs="ungrouped" :folders="folders" :folder-name="folderName" @move="moveToFolder" @create-folder="(id, name) => addFolderAndMove(name, id)" @archive="archive" @restore="restore" />
      </div>
    </template>
  </section>
</template>

<style scoped>
.requests {
  display: grid;
  gap: 16px;
}

.head {
  display: grid;
  gap: 4px;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.count {
  padding: 2px 10px;
  border-radius: var(--radius-tag);
  background: var(--primary-tint);
  color: var(--primary);
  font-size: 12px;
  font-weight: 600;
}

.head p {
  font-size: 13px;
  color: var(--text-secondary);
}

.loose {
  display: grid;
  gap: 10px;
  border: 1px dashed transparent;
  border-radius: var(--radius-lg);
}

.loose.over {
  border-color: var(--primary);
  background: var(--primary-tint);
}

.label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
}

.empty {
  padding: 32px 0;
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
}
</style>
