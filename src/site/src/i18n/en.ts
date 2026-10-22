/** Message per CLDR plural category (Czech also needs `few`). */
export interface PluralForms {
  one: string;
  few?: string;
  other: string;
}

export const en = {
  meta: {
    title: "subt-ai-tles — Context-aware subtitle translation for any LLM",
    description:
      "Open-source, self-hosted tool that translates .srt files with an LLM of your choice — keeping every timecode intact.",
  },
  header: {
    license: "MIT",
    star: "Star",
    githubLabel: "subt-ai-tles on GitHub",
    language: "Language",
    nav: "Primary",
  },
  hero: {
    badge: "Open-Source & Self-Hosted Subtitle Translation",
    titleBefore: "Context-Aware Subtitle Translation for",
    titleAccent: "Any LLM",
    subtitle:
      "A lightweight, open-source tool that translates .srt files with the model of your choice. OpenAI works today; Ollama, Claude and local llama.cpp are on the way. Zero vendor lock-in, zero broken timecodes.",
    deploy: "Deploy with Docker",
    star: "Star on GitHub",
    trust: [
      "100% Free & Open Source (MIT)",
      "Bring Your Own API Key",
      "Self-Hosted & Local-First",
      "Exact Millisecond Sync",
    ],
  },
  preview: {
    ariaLabel: "Preview of the subtitle editor",
    address: "localhost:9142",
    back: "Back to My Requests",
    summary: {
      label: "File summary",
      fileName: "episode_04_tokyo_heist.srt",
      model: "Model: gpt-5-nano",
      confidence: "94% confident",
      ready: "Ready",
      pair: "Linguistic pair",
      pairValue: "EN → CS (Czech)",
      density: "Density & cues",
      lines: { one: "{count} line", other: "{count} lines" } as PluralForms,
      runningTime: "Running time",
      runningTimeValue: "42m 18s",
      completed: "Completed",
      completedValue: "Today, 21:14",
      download: "Download .srt",
      copy: "Copy SRT to clipboard",
    },
    search: { placeholder: "Search line text or #cue number...", label: "Search lines" },
    filters: {
      label: "Filter lines",
      all: "All lines",
      modified: "Modified",
      flagged: "Flagged",
      cps: "High CPS",
    },
    cue: {
      optionActive: "Option {n} active",
      modified: "Modified",
      highCps: "High CPS",
      source: "EN (SOURCE)",
      target: "CS (TARGET)",
      unsaved: "Unsaved",
      edited: "Edited",
      autoTuned: "Auto-tuned",
      editLabel: "Edit translation",
      retranslate: "Re-translate",
      close: "Close",
      done: "Done",
      manualEdit: "Manual edit",
      edit: "Edit",
      accept: "Accept",
      discard: "Discard",
      flag: "Flag line",
      unflag: "Remove flag",
      retranslated: "Re-translated {ago}",
      justNow: "just now",
      seconds: "{n}s",
    },
    variants: {
      title: "ALTERNATIVE AI RENDERINGS",
      hint: "Click to apply",
      option: "Option {n}: {label} ({chars})",
      labels: ["Literal", "Natural", "Casual"],
      chars: { one: "{count} char", other: "{count} chars" } as PluralForms,
      placeholder: "e.g. Make it more casual slang...",
      promptLabel: "Custom context prompt",
      run: "Run",
    },
    actionBar: { download: "Download complete SRT", sync: "Re-sync all lines" },
  },
  features: {
    eyebrow: "Why subt-ai-tles",
    title: "Engineered for Media Localization",
    subtitle: "Designed specifically to solve dialogue flow, line timing, and model independence.",
    cards: [
      {
        icon: "brain",
        tint: "violet",
        title: "Contextual Dialogue Memory",
        text: "Translates scenes as a coherent narrative, preserving callbacks, character dynamics, and tone across whole episodes instead of fragmented cues.",
        tag: "Whole-file context memory",
      },
      {
        icon: "clock",
        tint: "cyan",
        title: "Strict Timecode Invariance",
        text: "Designed so that timecodes and cue sequences never drift. Millisecond timestamps stay exactly as they were in the source file.",
        tag: "Zero desync or broken tags",
      },
      {
        icon: "nodes",
        tint: "amber",
        title: "Use Any Model",
        text: "OpenAI is supported out of the box, with Ollama, local LLMs, Anthropic and custom OpenAI-compatible endpoints planned. Zero vendor lock-in.",
        tag: "OpenAI now • Ollama & Claude next",
      },
      {
        icon: "gauge",
        tint: "blue",
        title: "CPS & Reading Speed Safety",
        text: "Checks characters-per-second against human reading speeds and flags pacing violations before playback.",
        tag: "Standard CPS threshold validation",
      },
      {
        icon: "shield",
        tint: "green",
        title: "Self-Hosted & Private",
        text: "Runs on your own machine or private server. Files, history and cache stay on your hardware; only the text being translated goes to the model provider you choose.",
        tag: "Your data, your server",
      },
      {
        icon: "terminal",
        tint: "violet",
        title: "Single Command Deployment",
        text: "Runs via Docker Compose with no external database server — SQLite lives on a volume. Start translating in minutes.",
        tag: "docker compose up -d --build",
      },
    ],
  },
  workflow: {
    eyebrow: "Simple workflow",
    title: "From source script to translated subtitles in 3 steps",
    steps: [
      {
        title: "Drop your .srt file",
        text: "Instant local parsing and syntax validation. Auto-detects encodings, timing indices, and cue structure.",
        tag: "Supports .srt",
        tagTone: "neutral",
      },
      {
        title: "Select model, language & tone",
        text: "Native OpenAI API support works out of the box, with Ollama, Claude and local endpoints planned. Choose your target language and desired tone.",
        tag: "OpenAI supported • Ollama & Claude planned",
        tagTone: "success",
      },
      {
        title: "Review diff & export clean .srt",
        text: "Inspect alternate renderings, check CPS warnings, and download timestamp-accurate subtitle files ready for playback.",
        tag: "Instant clean export",
        tagTone: "neutral",
      },
    ],
  },
  start: {
    eyebrow: "Get started in seconds",
    title: "Run locally with Docker Compose",
    subtitle: "Spin up the web UI on localhost in one go. No database server to set up.",
    terminalLabel: "bash",
    copy: "Copy",
    copied: "Copied!",
    after: "Then open http://localhost:9142",
    checklist: [
      "Single docker-compose.yml",
      "No external database required",
      "MIT Licensed",
    ],
  },
  footer: {
    description:
      "A simple, open-source subtitle translation tool for creators, translators, and developers. Built for the community under the MIT license.",
    github: "GitHub",
    changelog: "Release Notes / Changelog",
    license: "License (MIT)",
    copyright: "subt-ai-tles project",
  },
};

export type Messages = typeof en;
