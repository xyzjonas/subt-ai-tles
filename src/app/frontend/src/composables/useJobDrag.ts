import { ref } from "vue";

/** Marks a drag as carrying a request, so unrelated drags (files, links) are ignored. */
const JOB_DRAG_TYPE = "application/x-subtaitles-job";

export function startJobDrag(event: DragEvent, jobId: string) {
  if (!event.dataTransfer) return;
  event.dataTransfer.setData(JOB_DRAG_TYPE, jobId);
  event.dataTransfer.effectAllowed = "move";
}

/** Handlers that make an element accept dropped requests; `over` is true while one hovers. */
export function useJobDropTarget(onDrop: (jobId: string) => void) {
  const over = ref(false);
  const carriesJob = (e: DragEvent) => !!e.dataTransfer?.types.includes(JOB_DRAG_TYPE);

  return {
    over,
    handlers: {
      dragover(e: DragEvent) {
        if (!carriesJob(e)) return;
        e.preventDefault();
        over.value = true;
      },
      dragleave(e: DragEvent) {
        // moving onto a child fires dragleave on the target too: only reset when truly leaving
        if (!(e.currentTarget as Node).contains(e.relatedTarget as Node | null)) over.value = false;
      },
      drop(e: DragEvent) {
        over.value = false;
        const id = e.dataTransfer?.getData(JOB_DRAG_TYPE);
        if (!id) return;
        e.preventDefault();
        onDrop(id);
      },
    },
  };
}
