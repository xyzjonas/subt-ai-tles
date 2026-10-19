import type { Job } from "../api/types";

/** One-line description of what a processing job is doing right now. */
export function stageLabel(job: Job): string {
  switch (job.stage) {
    case "summarizing":
      return "Summarizing the story…";
    case "translating":
      return `Translating cues ${job.processedCues ?? 0}/${job.cueCount}`;
    default:
      return "Recognizing the title…";
  }
}
