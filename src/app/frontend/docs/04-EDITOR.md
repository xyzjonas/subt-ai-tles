# Feature & Screen Spec: 04 - Detail: Subtitle Editor & Review

## 1. Screen Metadata
- **Route / Title**: `Detail: Subtitle Editor & Review`
- **Shell Layout**: `mobile_stack` (Top App Bar with Back button `←`, NO bottom navigation dock; fixed bottom action bar)
- **Purpose**: Review completed subtitle translations cue-by-cue, compare source and target texts side-by-side or stacked, re-translate lines using alternative LLM prompts, manually adjust wording, and export final `.srt`.

---

## 2. Information Architecture & Component Hierarchy

### A. Top App Bar & Navigation
- **Header**:
  - Back Button (`←`).
  - Page Title: `Export & Format` with subhead `subt-ai-tles editor`.
  - Profile Avatar Button (`36x36px`).
- **Sub-Header Navigation Link**:
  - `← Back to My Requests` (13px, `#4f46e5`, medium font).

### B. Summary Metadata Card
- **File Header**:
  - Subtitle badge icon.
  - File Name: Monospaced `tokyo_midnight_run_part1.srt`.
  - Status Tag: `✓ Ready` mint green pill (`bg: #d1fae5`, `text: #065f46`).
  - Model & Confidence: `Model: LLM Subtitle Context v2.4` • `99.4% confident` (11px monospace).
- **Metadata Matrix (2x2 Grid)**:
  - Cell 1: `Linguistic Pair`: `EN → JA (Japanese)`.
  - Cell 2: `Density & Cues`: `842 lines`.
  - Cell 3: `Running Time`: `42m 18s`.
  - Cell 4: `Completed`: `Today at 14:20`.
- **Top Quick Actions**:
  - Button 1: Primary `⤓ Download .SRT` (`bg: #4f46e5`, `color: #ffffff`, `border-radius: 10px`, `flex: 1`).
  - Button 2: Copy to clipboard icon button.
  - Button 3: Share / export icon button.

### C. Search & Filter Bar
- **Search Input**:
  - Placeholder: `Search line text or #cue number...` + keyboard shortcut pill `⌘K`.
- **Filter Tabs**:
  - `All Lines (842)` (Active solid pill: `bg: #4f46e5`, `text: #ffffff`).
  - `Modified (2)` (Tag pill: `bg: #d1fae5`, `text: #065f46`).
  - `Flagged` (Flag icon pill).
  - `High CPS` (Warning filter for fast dialogue).

### D. Subtitle Cue Cards (The Core Review Feed)
Each cue card represents one timed subtitle dialogue chunk:

#### Standard Subtitle Cue Card (e.g. Cue #001, #002, #004)
- **Header Row**:
  - Cue Index: `#001` (monospaced pill, `#e0e7ff` bg, `#4338ca` text).
  - Timecode Range: `▷ 00:00:14,200 → 00:00:17,450` (12px monospace, `#0f172a`).
  - Status / Duration: `✓ Synced` (mint green) or `3.7s duration` (slate).
- **Content Blocks**:
  - Source Text Box:
    - Dot label: `● EN (Source)`.
    - Text: `"Wait, did you hear that engine rumble just now?"` (14px, `#1e293b`).
  - Target Translation Box:
    - Inset container (`bg: #ffffff` or `#f8fafc`, `border: 1px solid #e2e8f0`, `border-radius: 8px`, `padding: 10px 12px`).
    - Dot label: `● JA (Target)` with right-aligned tag `Auto-tuned`.
    - Translated Text: `「待って、今のエンジンの轟音、聞こえた？」` (15px semibold, `#0f172a`).
- **Footer Actions**:
  - `↻ Re-translate` button (opens alternative suggestions or prompt input).
  - `✎ Edit` button (swaps translated text to editable textarea).
  - Bookmark / flag button (ribbon icon).

#### Expanded / Interactive Cue Card (e.g. Cue #003)
- **Visual Cue**: Elevated border (`2px solid #4f46e5`), subtle electric shadow, and `Option 2 Active` pill tag.
- **Header**: `#003 || 00:00:23,050 → 00:00:25,900`.
- **Source & Current Target**:
  - Source: `"Step on it before we lose them!"`
  - Current Target: `「見失う前に踏み込め！」`
- **Alternative AI Renderings (LLM Multi-Prompt Picker)**:
  - Header: `✦ Alternative AI Renderings` with hint `Click to apply`.
  - **Option 1: Literal (11 chars)**:
    - Text: `彼らを見失う前に急げ！`
  - **Option 2: Punchy / Action (9 chars - Active)**:
    - Text: `見失う前に踏み込め！` with checkmark icon `✓`.
    - Styling: `bg: #ede9fe`, `border: 1px solid #4f46e5`, `text: #3730a3`.
  - **Option 3: Shorter (7 chars)**:
    - Text: `撒かれるな、追え！`
- **Custom Context Prompt Input**:
  - Text input: `e.g. Make it more casual slang...` + `▷ Run` button (`bg: #4f46e5`).
- **Card Action Bar**:
  - `✎ Manual Edit` button | Metadata: `Re-translated 4m ago`.

### E. Persistent Floating Bottom Action Bar
- **Sticky Footer Bar**:
  - Full-width container docked at viewport bottom with blur backdrop / solid surface.
  - Left Primary CTA: `✓ Download Complete SRT` (`bg: #4f46e5`, `color: #ffffff`, `height: 48px`, `border-radius: 12px`, bold).
  - Right Quick Button: Refresh / re-sync all lines (`36x36px` icon button).

---

## 3. Interaction & Agent Implementation Logic
1. **Re-translate Workflow**:
   - Tapping `Re-translate` on any cue requests 3 variants from the backend (e.g. Literal, Stylized/Action, Compact/Short).
   - Selecting a variant immediately updates the target text and marks the cue as `Modified`.
2. **Inline Manual Edit**:
   - Tapping `Edit` replaces the target `<p>` tag with a `<textarea>` with matching line-height, auto-focused.
   - Blur or `Done` button saves changes and increments `Modified` count in filter tabs.
3. **Complete SRT Compilation**:
   - Tapping `Download Complete SRT` compiles all 842 cues (including manual edits and chosen alternatives) back into valid `.srt` format:
     ```text
     1
     00:00:14,200 --> 00:00:17,450
     「待って、今のエンジンの轟音、聞こえた？」
     ```
   - Triggers direct file download.
