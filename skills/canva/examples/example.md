# Canva Design System

> Visual creation platform. Vivid purple-blue gradient, generous spacing, friendly geometry.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#f4f5f7` | ![#f4f5f7](https://via.placeholder.com/20/f4f5f7/f4f5f7) |
| `--fg` | `#ff5757` | ![#ff5757](https://via.placeholder.com/20/ff5757/ff5757) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e1e3e6` | ![#e1e3e6](https://via.placeholder.com/20/e1e3e6/e1e3e6) |
| `--accent` | `#7d2ae8` | ![#7d2ae8](https://via.placeholder.com/20/7d2ae8/7d2ae8) |

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
  --surface: #f4f5f7;
  --fg: #ff5757;
  --muted: #6B6B6B;
  --border: #e1e3e6;
  --accent: #7d2ae8;
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

Generated from [`canva/DESIGN.md`](../canva/DESIGN.md)
