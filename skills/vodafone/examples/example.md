# Vodafone Design System

> Global telecom brand. Monumental uppercase display, Vodafone Red chapter bands.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#e60000` | ![#e60000](https://via.placeholder.com/20/e60000/e60000) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#7e7e7e` | ![#7e7e7e](https://via.placeholder.com/20/7e7e7e/7e7e7e) |
| `--border` | `#e60000` | ![#e60000](https://via.placeholder.com/20/e60000/e60000) |
| `--accent` | `#3860be` | ![#3860be](https://via.placeholder.com/20/3860be/3860be) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #e60000;
  --fg: #111111;
  --muted: #7e7e7e;
  --border: #e60000;
  --accent: #3860be;
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

Generated from [`vodafone/DESIGN.md`](../vodafone/DESIGN.md)
