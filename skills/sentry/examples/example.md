# Sentry Design System

> Error monitoring. Dark dashboard, data-dense, pink-purple accent.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#e5e7eb` | ![#e5e7eb](https://via.placeholder.com/20/e5e7eb/e5e7eb) |
| `--fg` | `#fa7faa` | ![#fa7faa](https://via.placeholder.com/20/fa7faa/fa7faa) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#cfcfdb` | ![#cfcfdb](https://via.placeholder.com/20/cfcfdb/cfcfdb) |
| `--accent` | `#1f1633` | ![#1f1633](https://via.placeholder.com/20/1f1633/1f1633) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Dammit Sans` |
| Body | `system-ui, sans-serif` |
| Monospace | `Monaco` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #e5e7eb;
  --fg: #fa7faa;
  --muted: #6B6B6B;
  --border: #cfcfdb;
  --accent: #1f1633;
  --font-display: Dammit Sans;
  --font-body: system-ui, sans-serif;
  --font-mono: Monaco;
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

Generated from [`sentry/DESIGN.md`](../sentry/DESIGN.md)
