# The Verge Design System

> Tech editorial media. Acid-mint and ultraviolet accents, Manuka display, rave-flyer story tiles.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#2d2d2d` | ![#2d2d2d](https://via.placeholder.com/20/2d2d2d/2d2d2d) |
| `--fg` | `#3860be` | ![#3860be](https://via.placeholder.com/20/3860be/3860be) |
| `--muted` | `#949494` | ![#949494](https://via.placeholder.com/20/949494/949494) |
| `--border` | `#309875` | ![#309875](https://via.placeholder.com/20/309875/309875) |
| `--accent` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `-0.16px` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #2d2d2d;
  --fg: #3860be;
  --muted: #949494;
  --border: #309875;
  --accent: #ffffff;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: -0.16px;
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

Generated from [`theverge/DESIGN.md`](../theverge/DESIGN.md)
