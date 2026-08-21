# Intercom Design System

> Customer messaging. Friendly blue palette, conversational UI patterns.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#ff2067` | ![#ff2067](https://via.placeholder.com/20/ff2067/ff2067) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#dedbd6` | ![#dedbd6](https://via.placeholder.com/20/dedbd6/dedbd6) |
| `--accent` | `#65b5ff` | ![#65b5ff](https://via.placeholder.com/20/65b5ff/65b5ff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `SaansMono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #ff2067;
  --muted: #6B6B6B;
  --border: #dedbd6;
  --accent: #65b5ff;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: SaansMono;
}
```

## Component Examples

### Button

```html
<button class="btn btn-primary">Get Started</button>
<button class="btn btn-secondary">Learn More</button>
```

```css
.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: var(--accent);
  color: white;
  border: none;
}

.btn-secondary {
  background: transparent;
  color: var(--fg);
  border: 1px solid var(--border);
}
```

### Card

```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</div>
```

```css
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
}
```

## Layout

- **Max width:** 1200px
- **Grid:** 12 columns
- **Gutters:** 24px
- **Section spacing:** 80px (desktop), 48px (tablet), 32px (mobile)

## Source

Generated from [`intercom/DESIGN.md`](../intercom/DESIGN.md)
