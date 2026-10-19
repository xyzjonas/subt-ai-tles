# Feature & Screen Spec: 02 - My Requests (History View)

## 1. Screen Metadata
- **Route / Title**: `My Requests - subt-ai-tles`
- **Shell Layout**: `mobile_tab` (Top App Bar + Persistent Bottom Dock with active tab on "My Requests")
- **Purpose**: Centralized dashboard to view, search, filter, and access all translation requests, whether currently running or completed.

---

## 2. Information Architecture & Component Hierarchy

### A. Top App Bar (Header)
- **Brand Identity**: Logo emblem + `subt-ai-tles` with subhead `My Requests`.
- **Status Indicator**: Model status badge `LLM v2.4 Active`.
- **Avatar Button**: User profile icon.

### B. Header Summary & Search Bar
- **Page Header**:
  - Title: `Translation History` (22px bold, `#0f172a`).
  - Task Count Pill: `● 4 tasks` (`bg: #ede9fe`, `text: #4f46e5`, font: 12px semibold).
  - Subhead: "Review, track, and export active subtitle jobs." (13px, `#475569`).
- **Global Search Input**:
  - Magnifying glass icon + input with placeholder: `Search files or languages...`
  - Styling: Pure white background, `border: 1px solid #e2e8f0`, `border-radius: 10px`, inset padding.
- **Segmented Filter Tabs**:
  - Full-width pill segment container (`bg: #f1f4f9`, `padding: 4px`, `border-radius: 10px`).
  - Options:
    - `Processing (1)`
    - `Completed (3)`
  - Active tab receives white card background with subtle shadow or electric primary tint.

### C. Active / Processing Job Cards
- **Card Styling**:
  - Surface: Pure white card with highlighted energetic left border accent (amber `#d97706` or electric `#4f46e5` 4px border-left).
  - Inset padding: `16px`.
- **Card Content**:
  - Icon: File/subtitle badge.
  - File Name: Monospaced font (`the_last_voyage_s01e02.srt`), font-weight 600.
  - Relative Timestamp: `2 mins ago` (right-aligned, `#64748b`).
  - Language Route Badge: `EN → ES (Spanish)` in subdued pill (`bg: #e0e7ff`, `text: #3730a3`).
  - Live Status Pill: `● Processing 68% • 512 / 750 lines` (`bg: #fef3c7`, `text: #92400e`).
  - Linear Progress Bar:
    - Track: `#f1f5f9` (4px height, rounded).
    - Fill: `#d97706` or `#4f46e5` reflecting exact percentage (68%).
  - Active Step Callout:
    - Live sync icon `🔁` + `AI translation engine translating chunk #7` (11px monospace).
  - Tap Affordance: Right chevron `>` indicating navigation to progress detail.

### D. Completed Job Cards
- **Card Styling**: Pure white surface, `1px solid #e2e8f0` border, `12px` border-radius.
- **Card Content**:
  - Icon: Subtitle reel icon.
  - File Name: Monospaced (`tokyo_midnight_run_part1...`, `tech_keynote_presentation...`).
  - Timestamp: `Today, 14:20` or `Yesterday, 19:05`.
  - Language Route Badge: `EN → JA (Japanese)` or `EN → DE (German)`.
  - Status Tag: `✓ Completed • 842 lines` in mint green (`bg: #ecfdf5`, `text: #065f46`).
  - Model Sync Line: `Synced with Whisper v3` or `Synced with GPT-4o Audio` (11px monospace, `#64748b`).
  - Direct Action Button:
    - Primary CTA pill: `⤓ Download` (`background: #4f46e5`, `color: #ffffff`, `border-radius: 8px`, `font-size: 12px semibold`).
    - Right navigation chevron `>` to open Subtitle Editor & Review.

### E. Persistent Bottom Navigation Bar
- Fixed dock at bottom of viewport (`height: 64px`, `background: #ffffff`, `border-top: 1px solid #e2e8f0`).
- Tab 1: **Translate** (Plus icon + label `Translate`).
- Tab 2: **My Requests** (History icon + badge notification `3` + label `My Requests`, highlighted in `#4f46e5`).

---

## 3. Interaction & Agent Implementation Logic
1. **Card Click Action**:
   - If card status is `Processing`, route to `Detail: Translating (In Progress)`.
   - If card status is `Completed`, route to `Detail: Subtitle Editor & Review`.
2. **Download Button Shortcut**:
   - Tapping `Download` directly triggers immediate client-side download of the translated `.srt` without entering detail view.
3. **Search & Filter Behavior**:
   - Instant client-side text filtering against file names, language codes (`ES`, `JA`, `DE`), and timestamps.
