# Supabase Design System

> Open-source Firebase alternative. Dark emerald theme, code-first.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#efefef` | ![#efefef](https://via.placeholder.com/20/efefef/efefef) |
| `--surface` | `#4d4d4d` | ![#4d4d4d](https://via.placeholder.com/20/4d4d4d/4d4d4d) |
| `--fg` | `#00c573` | ![#00c573](https://via.placeholder.com/20/00c573/00c573) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#242424` | ![#242424](https://via.placeholder.com/20/242424/242424) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `text-transform: uppercase` |

## CSS Custom Properties

```css
:root {
  --bg: #efefef;
  --surface: #4d4d4d;
  --fg: #00c573;
  --muted: #6B6B6B;
  --border: #242424;
  --accent: #2F6FEB;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
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

Generated from [`supabase/DESIGN.md`](../supabase/DESIGN.md)
