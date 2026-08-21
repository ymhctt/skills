---
name: design-wechat
description: "Generate HTML or Markdown using the WeChat Design System design system. TRIGGER when: user mentions wechat, WeChat Design System, or asks to create UI/content with this design style. Also trigger for requests like 'design a page in wechat style' or 'use WeChat Design System design tokens'."
---

# WeChat Design System Design System

You are a design implementation agent. Your job is to generate production-ready HTML or polished Markdown that faithfully applies the **WeChat Design System** design system.

## Design System Specification

# WeChat Design System

> Category: Social & Messaging
> Brand visual language for WeChat Mini Programs, official accounts, and open ecosystem extensions.

## Brand Identity

WeChat's identity is built on simplicity, cleanness, and trust — reflecting its role as a super-app that connects people, services, and businesses.

---

## Color Palette

### Brand Colors

| Token | Hex | Usage |
|---|----|----|
| `--wechat-green` | `#07C160` | Primary brand, CTA buttons, active states |
| `--wechat-green-light` | `#10B160` | Hover state for primary actions |
| `--wechat-green-dark` | `#059050` | Pressed/active state |

### Chat Bubble Colors

| Token | Hex | Usage |
|---|----|----|
| `--wechat-bubble-self` | `#95EC69` | Outgoing message bubbles |
| `--wechat-bubble-other` | `#FFFFFF` | Incoming message bubbles |
| `--wechat-bubble-text` | `#1A1A1A` | Primary text in bubbles |

### UI Neutrals

| Token | Hex | Usage |
|---|----|----|
| `--wechat-bg` | `#EDEDED` | Page/app background |
| `--wechat-surface` | `#F7F7F7` | Card, modal surfaces |
| `--wechat-border` | `#E0E0E0` | Dividers, borders |
| `--wechat-ink` | `#1A1A1A` | Primary text |
| `--wechat-muted` | `#888888` | Secondary text, timestamps |

### Functional Colors

| Token | Hex | Usage |
|---|----|----|
| `--wechat-red` | `#FA5151` | Errors, destructive actions |
| `--wechat-orange` | `#FAB702` | Warnings |
| `--wechat-blue` | `#576B95` | Links, info states |

---

## Typography

### Font Stack

```
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Helvetica, Arial, sans-serif;
```

### Type Scale

| Role | Size | Weight | Line Height |
|---|---|---|---|
| Page Title | 18px | 600 | 1.3 |
| Section Header | 16px | 600 | 1.4 |
| Body Text | 15px | 400 | 1.6 |
| Secondary Text | 13px | 400 | 1.5 |
| Caption/Timestamp | 11px | 400 | 1.4 |
| Button Label | 16px | 500 | 1.0 |

---

## Spacing System

4px base unit.

| Token | Value |
|---|-----|
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 12px |
| `--space-lg` | 16px |
| `--space-xl` | 24px |
| `--space-2xl` | 32px |

### Border Radius

| Token | Value |
|---|-----|
| `--radius-sm` | 4px |
| `--radius-md` | 8px |
| `--radius-lg` | 16px |
| `--radius-bubble` | 16px (with directional corner clip) |
| `--radius-full` | 9999px (avatars, pills) |

---

## Components

### Chat Bubble

```css
.wechat-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: var(--radius-bubble);
  font-size: 15px;
  line-height: 1.6;
  position: relative;
}

.wechat-bubble.self {
  background: var(--wechat-bubble-self);
  color: var(--wechat-bubble-text);
  border-top-right-radius: 4px;
  margin-left: auto;
}

.wechat-bubble.other {
  background: var(--wechat-bubble-other);
  color: var(--wechat-bubble-text);
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
```

### Primary Button (Send / Confirm)

```css
.btn-wechat-primary {
  background: var(--wechat-green);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-wechat-primary:hover {
  background: var(--wechat-green-light);
}

.btn-wechat-primary:active {
  background: var(--wechat-green-dark);
}
```

### Tab Bar

```css
.tab-bar {
  display: flex;
  background: var(--wechat-surface);
  border-top: 1px solid var(--wechat-border);
  padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
}

.tab-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--wechat-muted);
  font-size: 10px;
  cursor: pointer;
  transition: color 0.15s;
}

.tab-bar-item.active {
  color: var(--wechat-green);
}

.tab-bar-item svg {
  width: 24px;
  height: 24px;
}
```

### Message Input Bar

```css
.input-bar {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
  background: var(--wechat-surface);
  border-top: 1px solid var(--wechat-border);
}

.input-bar textarea {
  flex: 1;
  min-height: 36px;
  max-height: 100px;
  padding: 8px 12px;
  background: var(--wechat-bg);
  border: 1px solid var(--wechat-border);
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  outline: none;
}

.input-bar textarea:focus {
  border-color: var(--wechat-green);
}
```

### Avatar

```css
.avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  object-fit: cover;
  background: var(--wechat-border);
}

.avatar.sm { width: 32px; height: 32px; }
.avatar.lg { width: 56px; height: 56px; }
```

### Timestamp Badge

```css
.timestamp {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--wechat-muted);
  text-align: center;
}
```

---

## Motion & Animation

| Token | Value |
|---|-----|
| `--duration-instant` | 100ms |
| `--duration-fast` | 200ms |
| `--duration-normal` | 300ms |
| `--ease-default` | cubic-bezier(0.25, 0.1, 0.25, 1) |

Chat message entry: fade-in + slight slide up, 200ms.

---

## Dark Mode

| Token | Light | Dark |
|---|---|---|
| `--wechat-bg` | `#EDEDED` | `#1A1A1A` |
| `--wechat-surface` | `#F7F7F7` | `#2C2C2C` |
| `--wechat-ink` | `#1A1A1A` | `#F7F7F7` |
| `--wechat-bubble-self` | `#95EC69` | `#4CAF50` |
| `--wechat-bubble-other` | `#FFFFFF` | `#2C2C2C` |

---

## Usage

```css
:root {
  --wechat-green: #07C160;
  --wechat-green-light: #10B160;
  --wechat-green-dark: #059050;
  --wechat-bubble-self: #95EC69;
  --wechat-bubble-other: #FFFFFF;
  --wechat-bubble-text: #1A1A1A;
  --wechat-bg: #EDEDED;
  --wechat-surface: #F7F7F7;
  --wechat-border: #E0E0E0;
  --wechat-ink: #1A1A1A;
  --wechat-muted: #888888;
  --wechat-red: #FA5151;
  --wechat-orange: #FAB702;
  --wechat-blue: #576B95;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-2xl: 32px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-bubble: 16px;
  --radius-full: 9999px;
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --ease-default: cubic-bezier(0.25, 0.1, 0.25, 1);
}
```


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
