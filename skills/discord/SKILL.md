---
name: design-discord
description: "Generate HTML or Markdown using the Discord design system. TRIGGER when: user mentions discord, Discord, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in discord style' or 'use Discord design tokens'."
---

# Discord Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **Discord** design system.

## Design System Specification

# Design System Inspired by Discord

> Category: Productivity & SaaS
> Voice / chat platform. Deep blurple, dark-first surfaces, playful accent moments.

## 1. Visual Theme & Atmosphere

Discord's product is engineered for evenings, raids, and group voice — so the entire surface is dark-first. The default canvas is the deep `Background Primary` (`#313338` light theme, `#1e1f22` dark theme), with chat columns layered on slightly lighter or darker shades to denote channels, threads, and side panels. The signature **Blurple** (`#5865f2`) is reserved for the brand mark, primary CTAs, mentions, and the "you" affordance — used sparingly so it pops against the muted neutrals.

Typography is **gg sans** (Discord's custom Whitney-replacement) for prose and chrome, with rounded geometric shapes that feel approachable but still legible at the small sizes a chat client demands. Headings step up incrementally; chat rows are tight (4–8px between message groups) so hours of scrollback feel scannable.

The shape language is rounded but not balloon-soft: 8px radii on cards, 4px on inputs, full pills on status badges and tags. Servers are rounded-square avatars at 48px that morph to circles on hover — a tiny piece of motion that has become part of the brand's identity.

**Key Characteristics:**
- Dark-first surfaces: `#1e1f22` / `#2b2d31` / `#313338` (3-step depth)
- Blurple `#5865f2` as the only saturated accent in the chat surface
- gg sans (Whitney-style) for all text — friendly, geometric, neutral
- Rounded-square server avatars (16px radius) that snap to circles on hover
- Tight chat-row spacing, generous side-panel padding
- Status dots: green online, yellow idle, red dnd, gray offline
- Pixel-snapped 1px dividers in subtle off-white at low alpha

## 2. Color Palette & Roles

### Primary
- **Blurple** (`#5865f2`): Brand primary, primary CTA, mention highlight.
- **Blurple Hover** (`#4752c4`): Hover/active for blurple.
- **Blurple Soft** (`#7289da`): Legacy blurple, secondary accent in marketing.

### Surface (Dark Theme — default)
- **Background Tertiary** (`#1e1f22`): Server list rail, deepest background.
- **Background Secondary** (`#2b2d31`): Channel sidebar, settings sidebar.
- **Background Primary** (`#313338`): Chat surface, message column.
- **Background Floating** (`#111214`): Floating popovers, tooltips, autocomplete.
- **Background Modifier Hover** (`rgba(78, 80, 88, 0.3)`): Hover overlay on rows.
- **Background Modifier Selected** (`rgba(78, 80, 88, 0.6)`): Active row.

### Surface (Light Theme)
- **Light Bg Primary** (`#ffffff`): Chat surface in light theme.
- **Light Bg Secondary** (`#f2f3f5`): Sidebar in light theme.
- **Light Bg Tertiary** (`#e3e5e8`): Deepest light surface.

### Text
- **Header Primary** (`#f2f3f5`): Channel headers, modal titles in dark theme.
- **Header Secondary** (`#b5bac1`): Muted headers.
- **Text Normal** (`#dbdee1`): Body text in dark theme — slightly cooler than pure white.
- **Text Muted** (`#949ba4`): Timestamps, server names, secondary metadata.
- **Text Link** (`#00a8fc`): Hyperlinks in messages — sky blue, distinct from blurple.
- **Channels Default** (`#80848e`): Inactive channel name in sidebar.

### Status & Semantic
- **Status Online** (`#23a55a`): Online dot, success states.
- **Status Idle** (`#f0b232`): Idle dot, away.
- **Status DND** (`#f23f43`): Do-not-disturb, also serves as destructive red.
- **Status Streaming** (`#593695`): "Streaming" purple.
- **Status Offline** (`#80848e`): Offline gray.
- **Mention Highlight** (`rgba(88, 101, 242, 0.1)`): Soft blurple wash on @mention rows.

### Border & Divider
- **Background Modifier Accent** (`rgba(255, 255, 255, 0.06)`): Standard divider in dark.
- **Border Subtle** (`#3f4147`): Solid divider for cards.

## 3. Typography Rules

### Font Family
- **Body / UI / Headings**: `gg sans`, with fallback: `"Helvetica Neue", Helvetica, Arial, sans-serif`
- **Display (legacy / Whitney)**: `Whitney`, with fallback: `gg sans`
- **Code / Mono**: `"gg mono"`, with fallback: `Consolas, Andale Mono, Courier New, Courier, monospace`

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display Hero | gg sans | 56px (3.5rem) | 800 | 1.1 | -0.02em | Marketing hero |
| Page Heading | gg sans | 24px (1.5rem) | 700 | 1.25 | normal | Settings/profile titles |
| Channel Name | gg sans | 16px (1rem) | 600 | 1.25 | normal | `#general`, channel header |
| Message Body | gg sans | 16px (1rem) | 400 | 1.375 | normal | Standard chat text |
| Username | gg sans | 16px (1rem) | 500 | 1.25 | normal | Author of a message |
| Timestamp | gg sans | 12px (0.75rem) | 500 | 1.25 | normal | "Today at 4:32 PM" |
| Sidebar Channel | gg sans | 16px (1rem) | 500 | 1.25 | normal | Channel list rows |
| Server Name | gg sans | 16px (1rem) | 600 | 1.25 | normal | Server header |
| Caption / Meta | gg sans | 12px (0.75rem) | 400 | 1.3 | 0.02em | Status text, edited tag |
| Code Inline | gg mono | 0.875em | 400 | inherit | normal | Inline `code` |
| Code Block | gg mono | 14px (0.875rem) | 400 | 1.5 | normal | ```triple-fenced``` block |

### Principles
- **Friendly geometry**: gg sans replaces Whitney with rounded terminals on a/g/s — the brand wants warmth without breaking legibility.
- **Weight contrast over color contrast**: hierarchy comes from 400→500→600→700→800 weight steps; the surface stays neutral.
- **16px body**: chat messages do not shrink below 16px. Density comes from line-height (1.375), not font size.

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#5865f2`
- Text: `#ffffff`
- Padding: 8px 16px
- Radius: 4px
- Hover: `#4752c4`
- Use: Primary CTAs, "Continue", "Join Server"

**Secondary**
- Background: `#4e5058`
- Text: `#ffffff`
- Padding: 8px 16px
- Radius: 4px
- Hover: `#6d6f78`

**Tertiary / Subtle (Link-style)**
- Background: transparent
- Text: `#dbdee1`
- Hover: text underlined, no background change

**Danger**
- Background: `#da373c`
- Text: `#ffffff`
- Hover: `#a12d2f`

### Inputs
- Background: `#1e1f22`
- Text: `#dbdee1`
- Border: 1px solid `#1e1f22`
- Radius: 4px
- Padding: 10px 12px
- Focus: border `#5865f2`

### Server Avatars
- Size: 48×48px
- Radius: 16px (rounded square) by default; transitions to 50% on hover and active.
- Active state: 4px white pill on the left edge of the icon column.

### Status Dots
- Size: 10×10px
- Border: 3px solid background-tertiary (creates the "notch" effect)
- Position: bottom-right of avatar.

### Cards / Embeds
- Background: `#2b2d31` (dark) or `#f2f3f5` (light)
- Left border: 4px solid embed accent color.
- Radius: 4px
- Padding: 8px 16px

### Mention Pill
- Background: `rgba(88, 101, 242, 0.3)`
- Text: `#c9cdfb`
- Padding: 0 2px
- Radius: 3px

## 5. Spacing & Layout

- **Base unit**: 4px. Scale: 4, 8, 12, 16, 20, 24, 32, 40.
- **Server rail**: 72px wide, fixed.
- **Channel sidebar**: 240px wide.
- **Member list**: 240px wide on desktop.
- **Chat column**: fluid, min 380px.

## 6. Motion

- **Duration**: 200ms for hover; 350ms for the avatar circle-morph; 80ms for tooltip fade.
- **Easing**: `cubic-bezier(0.215, 0.61, 0.355, 1)` for the avatar morph (snappy then settle).
- **Notification pulse**: 1.4s ease-in-out infinite on unread mention indicator.


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
