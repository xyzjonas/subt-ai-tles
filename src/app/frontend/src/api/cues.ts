import { getJob } from "./jobs";
import { delay } from "./stub";
import type { Cue, CueVariant } from "./types";

const SAMPLES: [source: string, target: string][] = [
  ["Wait, did you hear that engine rumble just now?", "待って、今のエンジンの轟音、聞こえた？"],
  ["Hold on tight, this is going to get bumpy.", "しっかりつかまれ、揺れるぞ。"],
  ["Step on it before we lose them!", "見失う前に踏み込め！"],
  ["I told you this city never sleeps.", "この街は眠らないって言っただろ。"],
  ["Turn left at the next intersection.", "次の交差点を左に曲がれ。"],
  ["We're running out of time.", "時間がない。"],
  ["Do you trust me?", "俺を信じるか？"],
  ["Nothing will ever be the same after tonight.", "今夜を境に、すべてが変わる。"],
];
const DURATIONS = [3250, 2850, 3700, 1100];

function generateCues(count: number): Cue[] {
  let start = 14200;
  return Array.from({ length: count }, (_, i): Cue => {
    const [source, target] = SAMPLES[i % SAMPLES.length];
    const end = start + DURATIONS[i % DURATIONS.length];
    const cue = { index: i + 1, start, end, source, target };
    start = end + 600;
    return cue;
  });
}

/** GET /api/jobs/:id/cues */
export async function listCues(jobId: string): Promise<Cue[]> {
  const { cueCount } = await getJob(jobId);
  return delay(generateCues(cueCount), 400);
}

/** GET /api/jobs/:id/cues/:index -> a single cue (the one currently being translated) */
export function getCue(_jobId: string, index: number): Promise<Cue> {
  return delay(generateCues(index)[index - 1], 50);
}

/** POST /api/jobs/:id/cues/:index/retranslate  { prompt? } -> variants */
export function retranslateCue(_jobId: string, cue: Cue, prompt?: string): Promise<CueVariant[]> {
  const text = cue.target.replace(/[。！？]$/, "");
  const variants: CueVariant[] = prompt
    ? [{ label: "Custom", text: `${text}（${prompt}）` }]
    : [
        { label: "Literal", text: `${text}。` },
        { label: "Punchy / Action", text: `${text}！` },
        { label: "Shorter", text: text.slice(0, Math.max(2, Math.ceil(text.length * 0.7))) + "！" },
      ];
  return delay(variants, 700);
}
