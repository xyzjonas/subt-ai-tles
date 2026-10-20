# Feature & Screen Spec: 01 - Landing Page & Subtitle Upload

## 1. Screen Metadata
- **Route / Title**: `Translate .SRT - subt-ai-tles`
- **Shell Layout**: `mobile_tab` (Top App Bar + Persistent Bottom Dock with active tab on "Translate")
- **Purpose**: Allow users to drag-and-drop or select an SRT subtitle file, pick target translation language, configure context/tone parameters, and kick off the AI translation job.

---

## 2. Information Architecture & Component Hierarchy

### A. Top App Bar (Header)
- **Brand Identity**: Application emblem + name `subt-ai-tles`, subtitle `Translate`.
- **Status Indicator**: Pill badge with pulsing green indicator dot: `LLM v2.4 Active` (Background: `#ecfdf5`, Text: `#065f46`, Border: `#a7f3d0`).
- **User Avatar**: Circular icon button (`36x36px`) leading to account/settings.

### B. Hero & Headline Section
- **Tag Badge**: Violet badge `✦ Contextual Neural Engine` (`bg: #ede9fe`, `text: #4f46e5`, font: 11px semibold).
- **H1 Header**: `Translate subtitles with AI` (24px, 700 weight, `#0f172a`).
- **Body / Subhead**: "Upload any .srt file, pick your languages, and let LLMs deliver contextual, synchronized translations." (13px, `#475569`).

### C. File Ingestion Zone (Drop / Selection Card)
- **Section Label**: `SOURCE SUBTITLE FILE` (11px, 600 weight, uppercase, `#475569`).
- **Drop Container**:
  - Elevated card with dashed or clean crisp outline (`border: 1.5px dashed #cbd5e1` or `1px solid #e2e8f0`).
  - Centered upload icon pill with purple tint.
  - Call-to-action text: `Tap to browse or drop .srt file` (15px semibold).
  - Validation hints: "Accepts .srt, UTF-8 encoded up to 25MB" (12px, `#64748b`).
  - Browse trigger button: `Select from device` (`bg: #ede9fe`, `text: #4f46e5`, `border-radius: 8px`).
- **Selected File Preview Card** (Active State):
  - Inset container (`bg: #f8fafc`, border: `1px solid #e2e8f0`, `border-radius: 10px`).
  - File icon, file name (`episode_04_tokyo_heist.srt` in JetBrains Mono / SF Mono).
  - File metadata: `142 KB • 842 dialogue cues`.
  - Remove / replace `×` dismiss button.
  - Validation tag: `Validated UTF-8` (green dot) and `Encoding: OK`.

### D. Language Pairing Selector
- **Section Label**: `LANGUAGE PAIRING` with right-aligned tag `文A LLM Translation`.
- **Source language**: not an input. The model infers it while translating; it is only displayed afterwards (job list, progress, editor).
- **Target Language (To)**:
  - Input card showing `To (Target)` label, Flag icon, and language name (e.g. `Japanese (日本語)`).
  - Change trigger text / chevron button (`Change`).
- **Quick Target Selector Pills**:
  - Horizontal scrollable list of quick presets: `Spanish`, `Japanese` (active: `bg: #ede9fe`, `text: #4f46e5`, `border: 1px solid #4f46e5`), `German`, `French`, `Italian`, etc.

### E. Translation Parameters (Context & Tone)
- **Collapsible / Card Container**:
  - Header with icon, label `Context & Tone`, sublabel `Casual / Natural Dialogue`, and toggle chevron.
  - Preset Selector Pills (3-column grid):
    1. **Casual / Slang** (Active: `bg: #ede9fe`, `text: #4f46e5`, `border: 1px solid #4f46e5`).
    2. **Formal** (`bg: #f1f4f9`, `text: #475569`).
    3. **Literal** (`bg: #f1f4f9`, `text: #475569`).
  - Feature Switch / Guardrail:
    - Clock icon + `Preserve line breaks & CPS safety` label + `Enabled` badge.

### F. Primary Action Bar & Estimation
- **Primary CTA Button**:
  - Label: `⚡ Translate Subtitles (LLM) →`
  - Specs: Full width, `height: 52px`, `border-radius: 12px`, `background: #4f46e5`, text `#ffffff` (bold, 15px), vibrant shadow.
- **Job Estimations Row**:
  - Left: `⏱ Est. processing: ~35s`
  - Right: `⚙ ~4,200 tokens`

### G. Recent Subtitle Jobs List
- **Header**: `Recent Subtitle Jobs` with right-aligned `View All` text link.
- **List Items**:
  - Compact cards with file icon, filename in monospace, language pair (`EN → ES`), cue count (`1,204 cues`), relative time (`2h ago`), and status badge (`Ready` in mint green).

---

## 3. Interaction & Agent Implementation Logic
1. **File Upload Handlers**:
   - Accepts `.srt` MIME type or text files. Validate timestamps format (`00:00:00,000 --> 00:00:00,000`).
   - Parse cue count and display in the file preview state.
2. **Submit Event**:
   - On clicking `Translate Subtitles (LLM)`, validate file presence and target language.
   - Redirect / push route to the `Detail: Translating (In Progress)` view passing the job ID.
