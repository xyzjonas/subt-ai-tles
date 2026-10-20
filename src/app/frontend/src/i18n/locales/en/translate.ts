export default {
  hero: {
    title: "Translate subtitles with AI",
    lead: "Upload any .srt file, pick your languages, and let LLMs deliver contextual, synchronized translations.",
  },
  file: {
    label: "Source subtitle file",
    reading: "Reading file…",
    prompt: "Tap to browse or drop .srt file",
    hint: "Accepts .srt, UTF-8 encoded up to {max} MB",
    browse: "Select from device",
    remove: "Remove file",
    cueCount: "{count} dialogue cue | {count} dialogue cues",
    validated: "Validated UTF-8",
    encodingOk: "Encoding: OK",
    unreadable: "Could not read file.",
    noTimestamps: "No valid SRT timestamps found.",
    size: { kb: "{n} KB", mb: "{n} MB" },
  },
  target: "Target language",
  action: {
    start: "Translate subtitles (LLM)",
    starting: "Starting…",
    startFailed: "Could not start the translation",
    estimate: "Est. processing: {value}",
    seconds: "~{n}s",
    tokens: "~{n} tokens",
  },
  recent: {
    title: "Recent subtitle jobs",
    viewAll: "View all",
  },
};
