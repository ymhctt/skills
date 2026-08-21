# PlayStation Design System

> Gaming console retail. Three-surface channel layout, quiet-authority display type, cyan hover-scale.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#6b6b6b` | ![#6b6b6b](https://via.placeholder.com/20/6b6b6b/6b6b6b) |
| `--fg` | `#1883fd` | ![#1883fd](https://via.placeholder.com/20/1883fd/1883fd) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#f3f3f3` | ![#f3f3f3](https://via.placeholder.com/20/f3f3f3/f3f3f3) |
| `--accent` | `#0070cc` | ![#0070cc](https://via.placeholder.com/20/0070cc/0070cc) |

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
  --surface: #6b6b6b;
  --fg: #1883fd;
  --muted: #6B6B6B;
  --border: #f3f3f3;
  --accent: #0070cc;
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

Generated from [`playstation/DESIGN.md`](../playstation/DESIGN.md)
