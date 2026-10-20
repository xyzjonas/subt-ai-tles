import type { Job } from "../api/types";
import { t } from "../i18n";

/** One-line description of what a processing job is doing right now. */
export function stageLabel(job: Job): string {
  switch (job.stage) {
    case "summarizing":
      return t("progress.stage.summarizing");
    case "translating":
      return t("progress.stage.translating", { done: job.processedCues ?? 0, total: job.cueCount });
    default:
      return t("progress.stage.recognizing");
  }
}
