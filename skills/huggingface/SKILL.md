---
name: design-huggingface
description: "Generate HTML or Markdown using the Hugging Face design system. TRIGGER when: user mentions huggingface, Hugging Face, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in huggingface style' or 'use Hugging Face design tokens'."
---

# Hugging Face Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **Hugging Face** design system.

## Design System Specification

# Design System Inspired by Hugging Face

> Category: AI & LLM
> ML community hub. Sunny yellow accent, monospace identity, cheerful and dense.

## 1. Visual Theme & Atmosphere

Hugging Face is the rare ML brand that refuses to look serious. The hub leans into a sunshine-yellow accent (`#ffd21e`), a cartoon hugging-face emoji as the logo, and a confident **IBM Plex Mono** voice that reads more like a community zine than a research lab. The page background is a clean off-white (`#fafafa`) with text in a deep slate (`#0d1117`), and the yellow appears in pull quotes, tags, "new" badges, and the model-card header strip — never as an entire surface, always as punctuation.

The typographic system is monospace-forward in a way few product brands attempt: **IBM Plex Mono** for headings and tags, **Source Sans Pro** (or Inter) for body. The mix gives every page a "config file is the README" vibe — fitting for a platform built around `.gitattributes` and `model-card.md`.

Shapes are crisp, not soft: 4–6px radii, 1px solid borders that announce themselves rather than hide. Tables are dense, with row hover in a faint gray (`#f3f4f6`). The brand emoji punctuates everything — chips, headings, even error states wear a 🤗 — so the system feels human even when displaying technical data.

**Key Characteristics:**
- Sunshine yellow `#ffd21e` as the lone saturated accent
- IBM Plex Mono for headings and tags; Source Sans Pro for body
- Off-white canvas (`#fafafa`) with crisp 1px borders (`#e5e7eb`)
- 4–6px radii — closer to brutalist than rounded
- Hugging-face emoji 🤗 used unironically as a system glyph
- Dense tables, minimal padding — a community hub for power users
- Color-coded model categories (NLP blue, vision green, audio purple)

## 2. Color Palette & Roles

### Primary
- **HF Yellow** (`#ffd21e`): Brand primary, badges, "new" pill, model-card header bar.
- **HF Yellow Deep** (`#f59e0b`): Hover/active for yellow.
- **HF Yellow Soft** (`#fff4cc`): Surface tint, callout background.

### Surface & Background
- **Canvas** (`#ffffff`): Primary page background.
- **Canvas Subtle** (`#fafafa`): Alternate section background, footer.
- **Canvas Inset** (`#f3f4f6`): Code block background, hover row.
- **Canvas Dark** (`#0d1117`): Dark theme background.

### Ink & Text
- **Ink Primary** (`#0d1117`): Primary text, headings.
- **Ink Secondary** (`#374151`): Body prose.
- **Ink Muted** (`#6b7280`): Captions, file paths, model authors.
- **Ink Inverse** (`#f9fafb`): Text on dark surface.

### Category Accents (Model Tasks)
- **NLP Blue** (`#2563eb`): Text/NLP task badges.
- **Vision Green** (`#16a34a`): Computer-vision task badges.
- **Audio Purple** (`#9333ea`): Audio/speech task badges.
- **Multimodal Pink** (`#db2777`): Multimodal/diffusion task badges.
- **Tabular Orange** (`#ea580c`): Tabular/structured task badges.

### Semantic
- **Success** (`#16a34a`): Build succeeded, deploy live.
- **Warning** (`#f59e0b`): Slow inference, rate limit.
- **Error** (`#dc2626`): Failed build, broken model.
- **Info** (`#2563eb`): Notice banner.

### Border
- **Border Default** (`#e5e7eb`): Standard 1px hairline.
- **Border Strong** (`#d1d5db`): Emphasized border on hover.
- **Border Subtle** (`#f3f4f6`): Inner divider.

## 3. Typography Rules

### Font Family
- **Display / UI / Headings / Tags**: `IBM Plex Mono`, with fallback: `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`
- **Body / Prose**: `Source Sans Pro`, with fallback: `Inter, system-ui, -apple-system, sans-serif`
- **Editorial (rare, blog only)**: `Source Serif Pro`, with fallback: `Georgia, serif`

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display | IBM Plex Mono | 48px (3rem) | 600 | 1.1 | -0.01em | Marketing hero |
| H1 | IBM Plex Mono | 32px (2rem) | 600 | 1.2 | normal | Page heading, model name |
| H2 | IBM Plex Mono | 24px (1.5rem) | 600 | 1.25 | normal | Section heading |
| H3 | IBM Plex Mono | 18px (1.125rem) | 600 | 1.3 | normal | Sub-section |
| Body Large | Source Sans Pro | 18px (1.125rem) | 400 | 1.6 | normal | Lede, blog intro |
| Body | Source Sans Pro | 15px (0.9375rem) | 400 | 1.55 | normal | Standard prose, model card |
| Caption | Source Sans Pro | 13px (0.8125rem) | 500 | 1.4 | 0.01em | Author byline, timestamp |
| Tag / Badge | IBM Plex Mono | 12px (0.75rem) | 500 | 1.2 | 0.02em | Task tags, framework chips |
| Code | IBM Plex Mono | 14px (0.875rem) | 400 | 1.55 | normal | Code blocks, inline `model_id` |

### Principles
- **Mono everywhere it matters**: nav links, headings, tags, and metadata are all monospaced. Sans is reserved for paragraphs of prose.
- **Weight under 600**: 600 is the cap; 700 is too loud against yellow. Hierarchy is size and color.
- **Tags read as code**: model tags use mono so they look like the strings developers will paste into Python.

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#0d1117`
- Text: `#ffffff`
- Padding: 8px 16px
- Radius: 6px
- Hover: `#374151`
- Use: "Use this model", primary forms.

**Yellow CTA**
- Background: `#ffd21e`
- Text: `#0d1117`
- Padding: 8px 16px
- Radius: 6px
- Hover: `#f59e0b`
- Use: "Pro upgrade", "Sponsor".

**Outline**
- Background: `#ffffff`
- Text: `#0d1117`
- Border: 1px solid `#e5e7eb`
- Hover: background `#f3f4f6`

### Cards / Model Cards
- Background: `#ffffff`
- Border: 1px solid `#e5e7eb`
- Radius: 6px
- Padding: 16px 20px
- Header strip: `#ffd21e` background, 4px tall, only on featured model cards.

### Inputs
- Background: `#ffffff`
- Border: 1px solid `#e5e7eb`
- Radius: 6px
- Padding: 8px 12px
- Focus: border `#0d1117`, ring `0 0 0 3px rgba(13,17,23,0.1)`

### Tags / Chips (Task / Framework)
- Background: category-tinted soft (`#dbeafe` for NLP, `#dcfce7` for vision, etc.)
- Text: matching strong category color.
- Padding: 2px 8px
- Radius: 4px
- Font: IBM Plex Mono 12px / 500

### Tables
- Header: background `#fafafa`, border-bottom 1px `#e5e7eb`.
- Row: border-bottom 1px `#f3f4f6`, hover `#f3f4f6`.
- Padding: 8px 16px per cell — dense by design.

## 5. Spacing & Layout

- **Base unit**: 4px. Scale: 4, 8, 12, 16, 24, 32, 48, 64.
- **Container**: max 1280px, 24px gutter.
- **Sidebar (model browser)**: 280px wide.
- **Section rhythm**: 64–96px vertical between major sections.

## 6. Motion

- **Duration**: 120ms for hover; 200ms for menu open.
- **Easing**: `ease-out`.
- **Tag pop**: a 1.05× scale on hover at 120ms — the only exception to flat-on-hover.


## Output Modes

### HTML Output (default for UI requests)
When the user asks for a page, component, landing page, dashboard, or any visual artifact:

1. Use the design specification above
2. Generate a single self-contained HTML file with:
   - All CSS in a `<style>` block using CSS custom properties from the design system
   - `:` root block with all color/typography tokens
   - Semantic HTML5 structure
   - Responsive layout
   - No external dependencies (fonts loaded via Google Fonts or system stacks)

### Markdown Output (default for documentation requests)
When the user asks for documentation, specs, or text content:

1. Use the design specification above
2. Generate Markdown that reflects the design system's:
   - Color references in code blocks
   - Typography specifications in tables
   - Component patterns as structured documentation

## Token Mapping

Standard CSS variable names to use:
- `--bg` → background
- `--surface` → card/elevated surfaces
- `--fg` → primary text
- `--muted` → secondary text
- `--border` → borders and dividers
- `--accent` → primary interactive color
- `--success`, `--warn`, `--danger` → semantic colors
- `--font-display` → headings
- `--font-body` → body text
- `--font-mono` → code/technical

## Quality Checks

Before outputting, verify:
- [ ] All colors reference the design system's palette (no invented colors)
- [ ] Typography uses specified font families
- [ ] Spacing follows the design system's scale
- [ ] Component styles match the documented patterns
- [ ] No patterns from the "Don't" section appear

## Example Usage

User: "Create a landing page hero section"
→ Generate HTML with hero using the system's color palette, typography, and spacing

User: "Document the color palette"
→ Generate Markdown table with all colors, hex values, and usage notes

User: "Build a pricing card component"
→ Generate HTML card component matching the system's card styling pattern
