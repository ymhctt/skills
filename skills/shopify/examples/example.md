# Shopify Design System

> E-commerce platform. Dark-first cinematic, neon green accent, ultra-light type.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--surface` | `#1E2C31` | ![#1E2C31](https://via.placeholder.com/20/1E2C31/1E2C31) |
| `--fg` | `#9797A2` | ![#9797A2](https://via.placeholder.com/20/9797A2/9797A2) |
| `--muted` | `#A1A1AA` | ![#A1A1AA](https://via.placeholder.com/20/A1A1AA/A1A1AA) |
| `--border` | `#E4E4E7` | ![#E4E4E7](https://via.placeholder.com/20/E4E4E7/E4E4E7) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #FFFFFF;
  --surface: #1E2C31;
  --fg: #9797A2;
  --muted: #A1A1AA;
  --border: #E4E4E7;
  --accent: #2F6FEB;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: monospace;
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

Generated from [`shopify/DESIGN.md`](../shopify/DESIGN.md)
