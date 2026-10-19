import { requestJson } from "./http";
import type { Cue, CueVariant } from "./types";

/** GET /api/jobs/:id/cues */
export function listCues(jobId: string): Promise<Cue[]> {
  return requestJson(`/jobs/${jobId}/cues`);
}

/** GET /api/jobs/:id/cues/:index -> a single cue (the one currently being translated) */
export function getCue(jobId: string, index: number): Promise<Cue> {
  return requestJson(`/jobs/${jobId}/cues/${index}`);
}

/** PATCH /api/jobs/:id/cues/:index  { target } -> the stored cue */
export function updateCue(jobId: string, index: number, target: string): Promise<Cue> {
  return requestJson(`/jobs/${jobId}/cues/${index}`, { method: "PATCH", body: { target } });
}

/** POST /api/jobs/:id/cues/:index/retranslate  { prompt? } -> variants */
export function retranslateCue(jobId: string, index: number, prompt?: string): Promise<CueVariant[]> {
  return requestJson(`/jobs/${jobId}/cues/${index}/retranslate`, { method: "POST", body: { prompt } });
}
