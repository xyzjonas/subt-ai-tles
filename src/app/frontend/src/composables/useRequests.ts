import { computed, onMounted, ref } from "vue";
import { createFolder, deleteFolder, listFolders, renameFolder } from "../api/folders";
import { listArchivedJobs, listJobs, updateJob } from "../api/jobs";
import type { Folder, Job, JobPatch } from "../api/types";
import { describeError } from "../i18n/apiErrors";
import { timeAgo, formatWhen } from "../utils/srt";

export type RequestTab = "processing" | "completed" | "archived";

/** A folder together with its requests in the current tab. */
export interface FolderSection {
  folder: Folder;
  jobs: Job[];
}

const byNewest = (a: Job, b: Job) => b.createdAt.localeCompare(a.createdAt);

export function useRequests() {
  const active = ref<Job[]>([]);
  const archived = ref<Job[]>([]);
  const folders = ref<Folder[]>([]);
  const query = ref("");
  const tab = ref<RequestTab>("processing");
  const loading = ref(true);
  const error = ref("");

  onMounted(async () => {
    try {
      [active.value, archived.value, folders.value] = await Promise.all([listJobs(), listArchivedJobs(), listFolders()]);
      if (!active.value.some((j) => j.status === "processing")) tab.value = "completed";
    } catch (e) {
      error.value = describeError(e, "errors.unknown");
    } finally {
      loading.value = false;
    }
  });

  const folderName = (id?: string) => folders.value.find((f) => f.id === id)?.name;

  const inTab = (job: Job) => {
    if (tab.value === "archived") return !!job.archivedAt;
    return (tab.value === "processing") === (job.status === "processing");
  };

  const counts = computed(() => ({
    processing: active.value.filter((j) => j.status === "processing").length,
    completed: active.value.filter((j) => j.status !== "processing").length,
    archived: archived.value.length,
  }));

  const matching = computed(() => {
    const q = query.value.trim().toLowerCase();
    const source = tab.value === "archived" ? archived.value : active.value;
    return source
      .filter(inTab)
      .filter(
        (j) =>
          !q ||
          [j.fileName, j.sourceLang ?? "", j.targetLang, folderName(j.folderId) ?? "", timeAgo(j.createdAt), formatWhen(j.createdAt)].some((f) =>
            f.toLowerCase().includes(q),
          ),
      );
  });

  /** Folders with their requests (all folders while not searching, so they stay drop targets). */
  const sections = computed<FolderSection[]>(() => {
    if (tab.value === "archived") return [];
    const searching = !!query.value.trim();
    return folders.value
      .map((folder) => ({ folder, jobs: matching.value.filter((j) => j.folderId === folder.id) }))
      .filter((s) => !searching || s.jobs.length);
  });

  /** Requests outside any folder; the archive is always flat. */
  const ungrouped = computed(() =>
    tab.value === "archived" ? matching.value : matching.value.filter((j) => !folders.value.some((f) => f.id === j.folderId)),
  );

  /** Runs a mutation, surfacing a failure instead of throwing into the event handler. */
  async function attempt<T>(action: () => Promise<T>): Promise<T | undefined> {
    error.value = "";
    try {
      return await action();
    } catch (e) {
      error.value = describeError(e, "errors.unknown");
    }
  }

  const findJob = (id: string) => active.value.find((j) => j.id === id) ?? archived.value.find((j) => j.id === id);

  function replace(updated: Job) {
    const wasArchived = !!findJob(updated.id)?.archivedAt;
    const from = wasArchived ? archived : active;
    const to = updated.archivedAt ? archived : active;
    from.value = from.value.filter((j) => j.id !== updated.id);
    to.value = [...to.value.filter((j) => j.id !== updated.id), updated].sort(byNewest);
  }

  async function patch(jobId: string, change: JobPatch) {
    const updated = await attempt(() => updateJob(jobId, change));
    if (updated) replace(updated);
  }

  const moveToFolder = (jobId: string, folderId: string | null) => {
    // dropping onto the folder it is already in is a no-op, not a request
    if ((findJob(jobId)?.folderId ?? null) === folderId) return;
    return patch(jobId, { folderId });
  };
  const archive = (jobId: string) => patch(jobId, { archived: true });
  const restore = (jobId: string) => patch(jobId, { archived: false });

  async function addFolder(name: string): Promise<Folder | undefined> {
    const folder = await attempt(() => createFolder(name));
    if (folder) folders.value = [...folders.value, folder].sort((a, b) => a.name.localeCompare(b.name));
    return folder;
  }

  async function addFolderAndMove(name: string, jobId: string) {
    const folder = await addFolder(name);
    if (folder) await moveToFolder(jobId, folder.id);
  }

  async function rename(folder: Folder, name: string) {
    const updated = await attempt(() => renameFolder(folder.id, name));
    if (updated) folders.value = folders.value.map((f) => (f.id === updated.id ? updated : f)).sort((a, b) => a.name.localeCompare(b.name));
  }

  async function removeFolder(folder: Folder) {
    if (!(await attempt(() => deleteFolder(folder.id).then(() => true)))) return;
    folders.value = folders.value.filter((f) => f.id !== folder.id);
    const ungroup = (j: Job): Job => (j.folderId === folder.id ? { ...j, folderId: undefined } : j);
    active.value = active.value.map(ungroup);
    archived.value = archived.value.map(ungroup);
  }

  return {
    active,
    folders,
    query,
    tab,
    loading,
    error,
    counts,
    sections,
    ungrouped,
    folderName,
    moveToFolder,
    archive,
    restore,
    addFolder,
    addFolderAndMove,
    rename,
    removeFolder,
  };
}
