import { ref } from "vue";

const KEY = "subtaitles.collapsedFolders";

function load(): Set<string> {
  try {
    const stored = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return new Set(Array.isArray(stored) ? stored.filter((id) => typeof id === "string") : []);
  } catch {
    return new Set();
  }
}

// shared, so every folder reads and writes the same stored set
const collapsed = ref(load());

/** Whether a folder is open; remembered in localStorage (folders start open). */
export function useFolderCollapse(folderId: () => string) {
  const isOpen = () => !collapsed.value.has(folderId());

  function setOpen(open: boolean) {
    if (open === isOpen()) return;
    const next = new Set(collapsed.value);
    if (open) next.delete(folderId());
    else next.add(folderId());
    collapsed.value = next;
    try {
      localStorage.setItem(KEY, JSON.stringify([...next]));
    } catch {
      // storage unavailable (private mode, quota): the state just won't persist
    }
  }

  return { isOpen, setOpen };
}
