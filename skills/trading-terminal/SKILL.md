---
name: design-trading-terminal
description: "Generate HTML or Markdown using the Trading Terminal Design System design system. TRIGGER when: user mentions trading-terminal, Trading Terminal Design System, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in trading-terminal style' or 'use Trading Terminal Design System design tokens'."
---

# Trading Terminal Design System Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **Trading Terminal Design System** design system.

## Design System Specification

# Trading Terminal Design System

> Category: Themed & Unique
> Bloomberg-style financial trading terminal. Dark-only, data-dense, cyan/coral buy/sell signals. Everything readable at a glance from two meters away.

## 1. Visual Theme & Atmosphere

A professional-grade financial data terminal. Dense, information-rich layouts designed for traders who need to monitor multiple markets simultaneously. Dark surfaces reduce eye strain during long sessions. Cyan accent (#00D4AA) signals positive/buy, coral (#FF4757) signals negative/sell. Everything readable at a glance from two meters away.

- **Visual style:** dense, data-first, professional
- **Color stance:** dark surfaces with high-contrast data colors
- **Design intent:** keep outputs recognizable to this style family while preserving usability and readability

### Prior Art

Bloomberg Terminal, Refinitiv Eikon, FactSet, TradingView Pro. All share: dark-only surfaces, monospace data fonts, tabular layouts with no decorative spacing, and color-coded buy/sell signals.

## 2. Color Palette & Roles

### Surface Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#0D0D0D` | Primary canvas |
| Surface | `#141414` | Elevated panels, cards |
| Surface Hover | `#1A1A1A` | Hover state for panels |
| Border | `#2A2A2A` | Panel separation |

### Data Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#00D4AA` | Positive values, buy signals, success |
| Gain | `#00D4AA` | Positive price movement |
| Loss | `#FF4757` | Negative price movement |
| Warning | `#FFB800` | Caution alerts, margin warnings |
| Neutral | `#808086` | Unchanged, secondary data |
| Text Primary | `#FFFFFF` | High-contrast primary text |
| Text Secondary | `#AAAAAA` | Labels, metadata |
| Text Tertiary | `#828282` | Timestamps, grid labels |

### Dark Mode

Default and only mode. Trading terminals operate in dim environments for focus.

```css
:root {
  --color-bg: #0D0D0D;
  --color-surface: #141414;
  --color-surface-hover: #1A1A1A;
  --color-border: #2A2A2A;
  --color-primary: #00D4AA;
  --color-gain: #00D4AA;
  --color-loss: #FF4757;
  --color-warning: #FFB800;
  --color-text: #FFFFFF;
  --color-text-secondary: #AAAAAA;
  --color-text-tertiary: #828282;
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px;
}
```

## 3. Typography Rules

| Role | Size | Weight | Line Height | Font |
|------|------|--------|-------------|------|
| Display | 28px | 600 | 1.0 | JetBrains Mono |
| Heading | 16px | 600 | 1.2 | Inter |
| Body | 14px | 400 | 1.3 | JetBrains Mono |
| Label | 12px | 500 | 1.0 | Inter, uppercase |
| Micro | 10px | 400 | 1.0 | JetBrains Mono |

**Font labels for catalog extraction:**

```
Display: "JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
Heading: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif
Body: "JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
Label: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif
Micro: "JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
Mono: "JetBrains Mono", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
```

## 4. Component Stylings

### Order Book Row

```css
.order-book-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: var(--space-1) 0;
  border-bottom: 1px solid var(--color-border);
}
.order-book-size { color: var(--color-text-secondary); text-align: right; }
.order-book-bid  { color: var(--color-gain); text-align: right; }
.order-book-ask  { color: var(--color-loss); text-align: right; }
```

### Price Card

```css
.price-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.price-card-label {
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  color: var(--color-text-secondary);
  letter-spacing: 0.05em;
}
.price-card-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.0;
}
.price-card-change {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
}
.price-card-change.positive { color: var(--color-gain); }
.price-card-change.negative { color: var(--color-loss); }
```

### Ticker Bar

Horizontal scrolling single-line ticker for market overview.

```css
.ticker-bar {
  display: flex;
  gap: var(--space-6);
  overflow-x: auto;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
}
```

## 5. Layout Principles

Grid-based dense layout. Multiple data columns visible simultaneously. Panels share borders, not gaps. No rounded corners — sharp edges communicate precision. The layout is tabular: rows of data, columns of similar data.

## 6. Depth & Elevation

Trading terminals use flat design with border-based separation — no shadows. Surface shifts (#141414 vs #0D0D0D) convey elevation. Thin borders (#2A2A2A) define panel boundaries without decorative elements.

## 7. Do's and Don'ts

- Do not use color alone to signal buy/sell — always pair with a directional icon or label
- Do not animate data values decoratively — traders need instant, stable reads
- Do not use rounded corners — sharp precision aesthetic only
- Do not use light mode — trading terminals operate in dim environments
- Do not show more than 5 price points in a column — cognitive overload reduces decision speed
- Do not use gradients — flat fills only

## 8. Responsive Behavior

Terminal layouts target desktop-first (1280px+). On narrower viewports, columns collapse from rightmost to leftmost, prioritizing price and change data. Below 768px, single-column stack with horizontal scroll for overflow data. No breakpoints alter the dark-only constraint.

## 9. Agent Prompt Guide

When generating a trading terminal interface, prompt the model to:
- Use JetBrains Mono for all numeric data; Inter for labels and headings
- Always show gain/loss values in monospace with color coding (#00D4AA green, #FF4757 red)
- No rounded corners on any element
- Use 100ms transitions for price updates, 150ms for hover states
- Never use light mode or bright backgrounds
- Include a horizontal ticker bar with scrolling price updates
- All data changes retain old value briefly before swapping to prevent flash blindness

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
