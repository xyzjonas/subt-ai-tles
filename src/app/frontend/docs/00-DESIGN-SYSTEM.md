# subt-ai-tles — Design System & Visual Specification

## 1. Product Overview & Identity
- **Application Name**: `subt-ai-tles`
- **Tagline**: AI-powered contextual subtitle translation for SRT files.
- **Visual Aesthetic**: Minimalist flat interface with electric, high-energy accents designed specifically for high-contrast light mode. Clean typographic hierarchy, generous whitespace, structured cards with subtle border definition, and tactile tactile micro-indicators (badges, tags, cues).

---

## 2. Color Palette & Theming (Electric Precision Studio)

### Surface & Background Tokens
- **Canvas / App Background**: `#f7f9fb` (Ultra-crisp cool neutral tint)
- **Card / Container Surfaces**: `#ffffff` (Pure crisp white with `1px solid #e2e8f0` or `#e8edf5` borders)
- **Secondary / Subdued Surface**: `#f1f4f9` (Subtle inset containers, secondary panels, inactive states)
- **Muted Contrast Surface**: `#e2e8f0` (Borders, divider rules, subtle tracks)

### Primary & Accent Colors
- **Primary Electric Brand**: `#4f46e5` (Electric Indigo / Vibrant Violet)
  - Hover / Active: `#4338ca`
  - Subtle Tint / Glow: `rgba(79, 70, 229, 0.08)` to `rgba(79, 70, 229, 0.15)`
- **Secondary Energetic Accent**: `#6366f1` / `#7c3aed` (Gradient highlights and live badge accents)
- **Status & Feedback**:
  - **Live / In Progress**: `#2563eb` (Blue) or `#d97706` (Amber/Processing)
  - **Completed / Ready / Success**: `#10b981` (Vibrant Emerald / Mint green, with `#ecfdf5` background)
  - **Warning / Alert**: `#f59e0b` (Warm Amber, with `#fffbeb` background)
  - **Destructive / Error**: `#ef4444` (Crimson red, with `#fef2f2` background)

### Typography & Neutrals
- **Primary Text (Heading / Body)**: `#0f172a` (Deep Slate / Near-black for maximum contrast)
- **Secondary Text (Labels, Metadata)**: `#475569` (Slate grey)
- **Tertiary / Placeholder Text**: `#94a3b8` (Muted silver)

---

## 3. Typography Rules
- **Primary Typeface**: `Plus Jakarta Sans`, system fallbacks: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
- **Code / Monospace**: `JetBrains Mono`, `"SF Mono"`, `Menlo`, `monospace` (Used for timestamps, cue numbers, SRT filenames, tokens, syntax elements).
- **Scale Hierarchy**:
  - **Page Titles**: `24px` / `1.25` line-height, bold (`font-weight: 700`), tight tracking (`-0.02em`).
  - **Section Headings**: `16px` – `18px`, semibold (`font-weight: 600`), tracking (`-0.01em`).
  - **Body / Labels**: `14px` / `1.4` line-height, regular to medium (`font-weight: 400` / `500`).
  - **Captions & Metadata**: `11px` – `12px`, uppercase or monospace, medium/semibold (`font-weight: 500` / `600`).
  - **Timecodes**: `12px` – `13px` monospace, medium (`font-weight: 500`).

---

## 4. Component Standards & Layout Anatomy

### Shell & Navigation
- **Header**: Compact top app bar with app logo pill, live model status pill (`LLM v2.4 Active` in light green), and round avatar icon button.
- **Bottom Navigation** (Mobile Tabs): Fixed 2-item dock with clear active indicator, icons, and badges (`Translate`, `My Requests [badge]`).
- **Modal / Stack Navigation**: Header with circular back button (`←`), page title, and contextual quick action (`Download`, `Share`, or `Format`).

### Buttons & Controls
- **Primary Action**: Full-width or auto, `height: 48px` – `52px`, `border-radius: 12px`, background `#4f46e5`, font color `#ffffff`, font-weight `600`, subtle electric drop shadow (`0 4px 14px rgba(79, 70, 229, 0.3)`).
- **Secondary / Action Pills**: `height: 36px` – `40px`, `border-radius: 8px` – `10px`, background `#f1f4f9` or `#ffffff`, border `1px solid #e2e8f0`, hover `#e2e8f0`.
- **Destructive Action**: `height: 44px`, background `#fee2e2`, text `#dc2626`, border `1px solid #fecaca`.

### Form & Input Controls
- **Search & Text Inputs**: `background: #ffffff`, `border: 1px solid #e2e8f0`, `border-radius: 10px`, inset padding `10px 14px`, focus ring `2px solid #4f46e5`.
- **Toggle Switches**: Compact iOS/Material hybrid style, electric primary fill when toggled on.
