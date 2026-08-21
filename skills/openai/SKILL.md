---
name: design-openai
description: "Generate HTML or Markdown using the OpenAI design system. TRIGGER when: user mentions openai, OpenAI, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in openai style' or 'use OpenAI design tokens'."
---

# OpenAI Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **OpenAI** design system.

## Design System Specification

# Design System Inspired by OpenAI

> Category: AI & LLM
> Calm, near-monochrome system anchored in deep teal-black with generous white space and editorial typography.

## 1. Visual Theme & Atmosphere

OpenAI's product surface reads like a research lab dressed for the public — clinical, restrained, deliberately quiet. The page background is a true white (`#ffffff`) layered against a near-black ink (`#0d0d0d`) with a subtle teal undertone, so even the text feels slightly cooled rather than aggressively dark. The result is a chromatic neutrality that puts model output, code, and prose front and center, not the chrome around them.

The signature move is the use of **Söhne** (or its system stand-in `inter`) at restrained weights — 400 for body, 500 for nav and labels, 600 for emphasis — paired with **Signifier**, a contemporary serif used for editorial display. Where most AI brands lean futuristic, OpenAI's serif headlines give the product a quietly literary tone, as if every announcement is an essay.

The shape system is uniformly soft: 8px–12px radii, 9999px pills for tags and chips, no harsh corners anywhere. Section transitions are denoted by whitespace rather than dividers; when borders appear they are `#e5e5e5` hairlines that read as the absence of color rather than its presence.

**Key Characteristics:**
- True white canvas (`#ffffff`) with deep teal-black ink (`#0d0d0d`)
- Söhne / Inter at modest weights (400, 500, 600) — restraint over assertion
- Signifier serif for editorial display headlines
- Soft 8–12px radii everywhere; 9999px pills for chips
- Hairline borders (`#e5e5e5`) used sparingly; whitespace as primary divider
- Single-color illustrations in deep teal — no gradients in marks
- Generous line-height (1.55–1.65) and tracking near zero

## 2. Color Palette & Roles

### Primary
- **Pure White** (`#ffffff`): Primary background, card surface, button background.
- **Ink Black** (`#0d0d0d`): Primary text, brand mark, primary CTA.
- **Soft Black** (`#1a1a1a`): Secondary heading, alternative ink for non-critical text.

### Surface & Background
- **Mist** (`#fafafa`): Section break background, footer surface.
- **Pearl** (`#f5f5f5`): Card surface, elevated panel.
- **Cloud** (`#ececec`): Disabled background, divider tint.

### Brand Accent
- **OpenAI Teal** (`#10a37f`): Brand primary, link, highlight badge — the lone color in an otherwise neutral system.
- **Teal Deep** (`#0a7a5e`): Hover and pressed state for the brand color.
- **Teal Soft** (`#e8f5f0`): Surface tint for success badges, highlight callouts.

### Neutrals & Text
- **Graphite** (`#3c3c3c`): Body text, default reading color.
- **Slate** (`#6e6e6e`): Secondary text, captions, metadata.
- **Ash** (`#9b9b9b`): Tertiary text, placeholder, disabled label.
- **Stone** (`#c4c4c4`): Decorative dividers, faint icons.

### Semantic & Border
- **Border Hairline** (`#e5e5e5`): Standard hairline separator.
- **Border Soft** (`#ededed`): Card outline on white surface.
- **Error** (`#ef4146`): Validation, destructive action.
- **Warning** (`#f5a623`): Soft amber for advisory states.
- **Info** (`#2563eb`): Informational link tone (used sparingly; teal still wins).

## 3. Typography Rules

### Font Family
- **Display / Editorial**: `Signifier`, with fallback: `'Source Serif Pro', Georgia, serif`
- **Body / UI**: `Söhne`, with fallback: `Inter, system-ui, -apple-system, 'Segoe UI', sans-serif`
- **Code / Mono**: `Söhne Mono`, with fallback: `ui-monospace, 'JetBrains Mono', Menlo, Consolas, monospace`

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display | Signifier | 56px (3.5rem) | 400 | 1.08 | -0.02em | Editorial hero, announcement titles |
| H1 | Söhne | 40px (2.5rem) | 600 | 1.15 | -0.01em | Page heading |
| H2 | Söhne | 28px (1.75rem) | 600 | 1.2 | -0.005em | Section heading |
| H3 | Söhne | 20px (1.25rem) | 600 | 1.3 | normal | Sub-section |
| Body Large | Söhne | 18px (1.125rem) | 400 | 1.6 | normal | Lede paragraphs |
| Body | Söhne | 16px (1rem) | 400 | 1.65 | normal | Standard reading text |
| Body Small | Söhne | 14px (0.875rem) | 400 | 1.55 | normal | Card body, dense UI |
| Caption | Söhne | 13px (0.8125rem) | 500 | 1.4 | 0.01em | Metadata, badges |
| Label | Söhne | 12px (0.75rem) | 500 | 1.3 | 0.04em | Eyebrow, uppercase nav links |
| Code | Söhne Mono | 14px (0.875rem) | 400 | 1.55 | normal | Code blocks, terminal output |

### Principles
- **Restraint as identity**: weights cap at 600; 700+ feels off-brand. Hierarchy comes from size and color, not weight.
- **Serif for soul, sans for system**: Signifier appears only in editorial display moments. The product UI is sans-only.
- **Negative tracking on display**: -0.02em on display sizes; tracking returns to zero by 16px.

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#0d0d0d`
- Text: `#ffffff`
- Padding: 10px 18px
- Radius: 9999px (full pill) on chips, 12px on rectangular CTAs
- Hover: `#1a1a1a` background
- Use: Primary CTA, "Try ChatGPT", "Sign in"

**Secondary**
- Background: `#ffffff`
- Text: `#0d0d0d`
- Border: 1px solid `#e5e5e5`
- Padding: 10px 18px
- Radius: 12px
- Hover: background `#fafafa`, border `#d4d4d4`

**Brand Accent**
- Background: `#10a37f`
- Text: `#ffffff`
- Padding: 10px 18px
- Radius: 12px
- Hover: `#0a7a5e`
- Use: Highlighted upgrade CTA, success path

### Cards
- Background: `#ffffff`
- Border: 1px solid `#ededed`
- Radius: 16px
- Padding: 24px–32px
- Shadow: none by default; on hover `0 4px 16px rgba(13,13,13,0.06)`

### Inputs
- Background: `#ffffff`
- Border: 1px solid `#e5e5e5`
- Radius: 12px
- Padding: 12px 14px
- Focus: border `#10a37f`, ring `0 0 0 3px rgba(16,163,127,0.12)`

### Pills & Tags
- Background: `#f5f5f5`
- Text: `#3c3c3c`
- Padding: 4px 10px
- Radius: 9999px
- Font: 12px / 500

## 5. Spacing & Layout

- **Base unit**: 4px. Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128.
- **Container**: max-width 1200px, 24px gutter on mobile, 48px on desktop.
- **Section rhythm**: 96–128px vertical between major sections; 64px on mobile.
- **Grid**: 12-column desktop, 4-column mobile, 24px gap.

## 6. Motion

- **Duration**: 150–220ms for hover; 280–360ms for layout transitions.
- **Easing**: `cubic-bezier(0.16, 1, 0.3, 1)` (smooth out) for entrances.
- **Restraint**: no parallax, no scroll-jacking. Subtle fade and translate only.


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
