# MongoDB Design System

> Document database. Green leaf branding, developer documentation focus.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#3d4f58` | ![#3d4f58](https://via.placeholder.com/20/3d4f58/3d4f58) |
| `--fg` | `#001e2b` | ![#001e2b](https://via.placeholder.com/20/001e2b/001e2b) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#006cfa` | ![#006cfa](https://via.placeholder.com/20/006cfa/006cfa) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `MongoDB Value Serif` |
| Body | `Euclid Circular A` |
| Monospace | `text-transform: uppercase` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #3d4f58;
  --fg: #001e2b;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #006cfa;
  --font-display: MongoDB Value Serif;
  --font-body: Euclid Circular A;
  --font-mono: text-transform: uppercase;
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

Generated from [`mongodb/DESIGN.md`](../mongodb/DESIGN.md)
