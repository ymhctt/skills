---
name: design-canva
description: "Generate HTML or Markdown using the Canva design system. TRIGGER when: user mentions canva, Canva, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in canva style' or 'use Canva design tokens'."
---

# Canva Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **Canva** design system.

## Design System Specification

# Design System Inspired by Canva

> Category: Design & Creative
> Visual creation platform. Vivid purple-blue gradient, generous spacing, friendly geometry.

## 1. Visual Theme & Atmosphere

Canva is the friendly face of design tools — the brand makes a point of looking inviting where Adobe looks intimidating. The page is built on a clean white canvas (`#ffffff`) with a signature **purple-to-blue gradient** (`#7d2ae8` → `#00c4cc`) used in the brand mark, hero buttons, and Pro/Magic moments. Surfaces are generously padded, edges are gently rounded (8–16px), and shadows are soft and cool-toned.

Typography uses **Canva Sans** (a custom geometric sans) for chrome and prose, with rounded letterforms that share DNA with brands like Airbnb and Asana. Weight contrast does the heavy lifting — 800 for hero display, 700 for section heads, 400 for body — while size hierarchy is more compressed than typical product brands so cards and templates read at a glance.

The shape system is ultra-soft: 12px on most cards, 16–20px on larger panels, 9999px on chips. Buttons are rectangles with a subtle elevation shadow (`0 2px 8px rgba(0,0,0,0.06)`) that grows on hover. Iconography is filled and rounded, never line-only — Canva's icons speak the same shape language as its UI.

**Key Characteristics:**
- White canvas with a violet-to-cyan gradient (`#7d2ae8` → `#00c4cc`)
- Canva Sans (rounded geometric) for everything; weight contrast over color
- 12–20px radii everywhere; 9999px pills for chips and tags
- Soft cool-toned shadows that grow on hover
- Filled rounded iconography — never outlined
- Vibrant secondary palette (coral, mint, tangerine) for category tags
- Pro/Magic moments lit by a static gradient — no animation

## 2. Color Palette & Roles

### Brand Gradient
- **Canva Purple** (`#7d2ae8`): Brand primary; gradient origin.
- **Canva Cyan** (`#00c4cc`): Brand secondary; gradient terminus.
- **Canva Pink** (`#ff5757`): Tertiary brand accent (Magic Studio).

### Surface
- **Canvas** (`#ffffff`): Primary background.
- **Surface Subtle** (`#f4f5f7`): Section break, sidebar.
- **Surface Inset** (`#e8eaed`): Disabled, inset block.
- **Surface Cool** (`#eef0fc`): Hover tint on purple-themed cards.

### Ink & Text
- **Ink Primary** (`#0e1318`): Primary text.
- **Ink Secondary** (`#3c4043`): Body prose.
- **Ink Muted** (`#5f6368`): Captions, descriptions.
- **Ink Faint** (`#9aa0a6`): Placeholder, disabled label.

### Semantic
- **Success** (`#00b894`): Saved, exported.
- **Warning** (`#ffb020`): Storage limit, advisory.
- **Error** (`#ff5757`): Validation, destructive.
- **Info** (`#0d99ff`): Tip, link.

### Category Accents (Template Tags)
- **Coral** (`#ff7059`): Social posts.
- **Tangerine** (`#ff9633`): Marketing.
- **Mint** (`#48c997`): Education.
- **Sky** (`#3ea6ff`): Business.
- **Lavender** (`#9b87f5`): Personal.

### Border
- **Border Default** (`#e1e3e6`): Standard hairline.
- **Border Strong** (`#c7cdd3`): Emphasized border, hover state.

## 3. Typography Rules

### Font Family
- **Display / UI / Body**: `Canva Sans`, with fallback: `'YS Text', system-ui, -apple-system, sans-serif`
- **Editorial (rare)**: `Canva Sans Display`, with fallback: `'Canva Sans', sans-serif`
- **Code (devtools only)**: `JetBrains Mono`, with fallback: `ui-monospace, Menlo, Consolas, monospace`

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Hero | Canva Sans | 64px (4rem) | 800 | 1.05 | -0.02em | Marketing hero, "Design anything." |
| H1 | Canva Sans | 36px (2.25rem) | 700 | 1.15 | -0.01em | Page heading |
| H2 | Canva Sans | 24px (1.5rem) | 700 | 1.2 | -0.005em | Section heading |
| H3 | Canva Sans | 18px (1.125rem) | 600 | 1.3 | normal | Sub-section, card title |
| Body Large | Canva Sans | 16px (1rem) | 400 | 1.55 | normal | Lede, marketing body |
| Body | Canva Sans | 14px (0.875rem) | 400 | 1.5 | normal | Standard UI prose |
| Caption | Canva Sans | 12px (0.75rem) | 500 | 1.4 | 0.005em | Metadata, hint text |
| Button | Canva Sans | 14px (0.875rem) | 600 | 1.2 | normal | Default button label |
| Tag | Canva Sans | 11px (0.6875rem) | 600 | 1.2 | 0.04em | Uppercase category chip |

### Principles
- **Weight contrast over color contrast**: hierarchy steps via 800→700→600→400; the surface stays neutral.
- **Tight line-height for cards**: card titles use 1.15–1.2 so a 3-line title still fits a 4:3 thumbnail.
- **No display serif**: Canva is sans-only across all surfaces; serifs appear only as user-selectable template fonts inside the editor.

## 4. Component Stylings

### Buttons

**Primary (Gradient)**
- Background: `linear-gradient(135deg, #7d2ae8, #00c4cc)`
- Text: `#ffffff`
- Padding: 12px 20px
- Radius: 8px
- Shadow: `0 2px 8px rgba(125, 42, 232, 0.2)`
- Hover: shadow grows to `0 4px 14px rgba(125, 42, 232, 0.3)`
- Use: hero CTAs, "Try Canva Pro"

**Primary (Solid Purple)**
- Background: `#7d2ae8`
- Text: `#ffffff`
- Padding: 12px 20px
- Radius: 8px
- Hover: `#6815d4`

**Secondary**
- Background: `#ffffff`
- Text: `#0e1318`
- Border: 1px solid `#e1e3e6`
- Radius: 8px
- Hover: background `#f4f5f7`, border `#c7cdd3`

**Subtle / Tertiary**
- Background: `rgba(125, 42, 232, 0.08)`
- Text: `#7d2ae8`
- Hover: background `rgba(125, 42, 232, 0.14)`

### Cards / Template Tiles
- Background: `#ffffff`
- Border: 1px solid `#e1e3e6`
- Radius: 12px
- Shadow at rest: `0 1px 3px rgba(0,0,0,0.04)`
- Shadow on hover: `0 8px 24px rgba(0,0,0,0.08)`, lift 2px
- Aspect ratio: thumbnail respects template (1:1, 4:3, 9:16)

### Inputs
- Background: `#ffffff`
- Border: 1px solid `#e1e3e6`
- Radius: 8px
- Padding: 10px 14px
- Focus: border `#7d2ae8`, ring `0 0 0 3px rgba(125, 42, 232, 0.16)`

### Chips / Tags
- Background: category-tinted soft.
- Text: matching strong category color.
- Padding: 4px 10px
- Radius: 9999px
- Font: 11px / 600 / uppercase

### Pro Badge
- Background: `linear-gradient(135deg, #7d2ae8, #ff5757)`
- Text: `#ffffff`
- Padding: 2px 8px
- Radius: 9999px
- Font: 10px / 700 / uppercase

## 5. Spacing & Layout

- **Base unit**: 4px. Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- **Container**: max 1320px, 32px gutter.
- **Sidebar (editor)**: 320px wide; collapses to 56px icons.
- **Card grid gap**: 16px on mobile, 24px on desktop.

## 6. Motion

- **Duration**: 180ms for hover; 280ms for menu open; 420ms for editor sidebar collapse.
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` (Material-style).
- **Card lift**: translateY(-2px) + shadow grow on hover, single transition.


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
