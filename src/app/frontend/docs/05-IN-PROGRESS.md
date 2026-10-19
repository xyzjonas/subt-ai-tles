# Feature & Screen Spec: 03 - Detail: Translating (In Progress)

## 1. Screen Metadata
- **Route / Title**: `Detail: Translating (In Progress)`
- **Shell Layout**: `mobile_stack` (Top App Bar with Back chevron `←`, NO bottom navigation bar)
- **Purpose**: Provide real-time transparency and reassurance while LLM translates subtitle cues in chunks, displaying live completion percentage, milestone checklist, live cue streaming, and cancellation controls.

---

## 2. Information Architecture & Component Hierarchy

### A. Top Navigation Bar (Stack Header)
- **Back Button**: Left-aligned circular arrow button (`←`) returning to "My Requests".
- **Screen Title**: `Editor & Calibration` with subtitle `subt-ai-tles editor`.
- **User Profile**: Circular avatar button (`36x36px`).

### B. Job Overview Card
- **File Identity**:
  - Subtitle file icon in purple pill container.
  - File Name: Monospaced `the_last_voyage_s01e02.srt`.
  - Live Status Tag: `● Live` pulsing green badge (`bg: #ecfdf5`, `text: #059669`).
  - Technical specs: `SubRip (.srt) • UTF-8 • Submitted 2 mins ago` (11px monospace).
- **Language Route Pill**:
  - Source box: `EN English` → Arrow `→` → Target box: `ES Spanish` | `750 cues`.

### C. Large Circular Progress Gauge (Hero Metric)
- **Circular Progress Ring**:
  - Diameter: `160px` – `180px` SVG circle gauge.
  - Background track: Soft electric tint (`#e0e7ff`, stroke: 12px).
  - Active fill: Solid electric indigo (`#4f46e5`, stroke: 12px, stroke-linecap: round).
  - Center Label:
    - Percentage: `68%` (32px font, 700 bold weight, `#0f172a`).
    - Subtitle: `510 / 750 lines` (13px, `#64748b`).
- **Live Action Tagline**:
  - Status indicator: Pulsing electric dot `● Translating dialogue nuances`.
  - Explanatory note: "Applying contextual colloquialisms and timing sync..." (13px, `#475569`).
- **Secondary Micro Linear Track**:
  - Subtle horizontal bar showing chunk batching progress.

### D. Pipeline Milestones (Step Checklist)
- **Header**: `Pipeline Milestones` with right-aligned `4 Steps` badge.
- **Step Items**:
  1. **Parsing SRT timecodes & syntax**:
     - Status: `✓ Done` | Green checkmark circle (`bg: #d1fae5`, `icon: #059669`).
     - Sublabel: `Validated 750 timecodes • Done` (11px monospace).
  2. **Contextual idiom & dialogue analysis**:
     - Status: `✓ Done` | Green checkmark circle.
     - Sublabel: `Character mapping confirmed • Done`.
  3. **Generating localized Spanish**:
     - Status: `Processing` | Spinning electric blue cycle icon (`bg: #ede9fe`, `icon: #4f46e5`).
     - Sublabel: `Translating lines 510-540 of 750...` (in progress indicator).
  4. **Timecode calibration & SRT compilation**:
     - Status: `Pending` | Muted circular dot (`bg: #f1f5f9`).
     - Sublabel: `Pending target completion`.

### E. Live Stream Streamer (Active Cue Inspector)
- **Container**: Card container with dark/light code block accent (`bg: #f8fafc`, `border: 1px solid #e2e8f0`).
- **Header**:
  - Terminal icon + label: `Live Stream Streamer`.
  - Active Cue Badge: `Cue #512` (`bg: #ede9fe`, `text: #4f46e5`, font: 11px monospace).
- **Cue Data**:
  - Timecode Bar: `00:04:12,100 ➔ 00:04:15,350` | `3.25s duration` (12px monospace).
  - Source Text (SRC): `"Hold on, we're almost through the storm!"` (italicized slate).
  - Target Translation (TGT): `¡Aguanta, ya casi salimos de la tormenta!` (bold slate with blinking electric cursor `█`).

### F. Controls & Notification Footer
- **Push Notification Toggle**:
  - Bell icon + text: `Notify when complete` / `Send push alert upon compilation`.
  - Toggle switch: Active electric indigo fill.
- **Destructive Action**:
  - Button: `⊗ Cancel Translation` (`bg: #fee2e2`, `text: #991b1b`, `border: 1px solid #fecaca`, `height: 44px`, `border-radius: 10px`).
  - Footnote: "Tokens consumed will reflect progress made" (11px, `#64748b`).

---

## 3. Interaction & Agent Implementation Logic
1. **Realtime Polling / WebSocket**:
   - In production, connect to a job status stream (`SSE` or `WebSocket`) updating percentage, active cue index, and milestone statuses.
2. **Auto-Navigation on Completion**:
   - Once percentage reaches 100% and Step 4 completes, auto-transition the view to `Detail: Subtitle Editor & Review`.
