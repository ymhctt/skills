---
name: design-default
description: "Generate HTML or Markdown using the Neutral Modern design system. TRIGGER when: user mentions default, Neutral Modern, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in default style' or 'use Neutral Modern design tokens'."
---

# Neutral Modern Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **Neutral Modern** design system.

## Design System Specification

# Neutral Modern

> Category: Starter
> A clean, product-oriented default. Use when the brief doesn't call for a
> specific mood — good for B2B tools, dashboards, and utility pages.

## Visual Theme & Atmosphere
Calm, functional, quietly confident. No ornament. Content-first, chrome-second.

## Color Palette & Roles
- **Background:** `#FAFAFA`
- **Foreground:** `#111111`
- **Accent:** `#2F6FEB` (cobalt) — primary CTAs, links, one hero element per screen
- **Muted:** `#6B6B6B` — secondary text, captions
- **Border:** `#E5E5E5`
- **Surface:** `#FFFFFF` — cards, modals
- **Success:** `#17A34A`, **Warn:** `#EAB308`, **Danger:** `#DC2626`
Never pure black; never pure white for backgrounds.

## Typography Rules
- **Display / headings:** `'Inter', -apple-system, system-ui, sans-serif`, weight 600
- **Body:** `'Inter', -apple-system, system-ui, sans-serif`, weight 400
- **Mono:** `ui-monospace, 'JetBrains Mono', monospace`
- Scale (px): 12 · 14 · 16 · 20 · 24 · 32 · 48 · 64
- Line-height: 1.5 for body, 1.2 for headings
- Letter-spacing: -0.01em on display sizes ≥32px

## Component Stylings
- **Buttons:** 8px radius, 10px padding-block, 16px padding-inline. Primary = cobalt fill, white label. Secondary = 1px border, transparent fill.
- **Cards:** white, 1px border, 12px radius, 20px internal padding, no shadow by default.
- **Inputs:** 1px border, 8px radius, 10px vertical padding, cobalt border on focus.
- **Links:** cobalt, no underline, underline on hover.

## Layout Principles
- 12-column grid, 1200px max-width, 24px gutters.
- Hero: 40–60vh. Content top-biased, never centered vertically.
- Sections: 80px top+bottom spacing desktop, 48px tablet, 32px phone.
- Use whitespace as the main separator. Dividers only between unrelated top-level sections.

## Depth & Elevation
Two levels only:
- **Flat (0):** default.
- **Raised (1):** dropdowns, modals, floating buttons. 2px y-offset, 8px blur, foreground at 8% opacity.
No neumorphism, no glassmorphism.

## Do's and Don'ts
- ✅ Let whitespace do the work.
- ✅ One accent element per screen.
- ✅ Sentence-case headings by default; title case only for brand names.
- ❌ No gradients (except the accent → accent-at-80% on a hero, sparingly).
- ❌ No drop shadows on inputs.
- ❌ No more than three type sizes on one screen.

## Responsive Behavior
- **Desktop ≥ 1024px:** 12-col grid.
- **Tablet 640–1023px:** 8-col grid, 16px gutters.
- **Phone < 640px:** 4-col grid, 12px gutters; hero drops to 40vh.

## Agent Prompt Guide
- When in doubt, subtract. Fewer boxes, less chrome, more space.
- Use the accent color sparingly — at most one hero accent and one CTA accent per screen.
- Do not invent hex values outside this palette. If the request needs one, surface a warning comment in the artifact and use the closest existing token.


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
