# WIRED Design System

> Tech magazine. Paper-white broadsheet density, custom serif display, mono kickers, ink-blue links.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#1a1a1a` | ![#1a1a1a](https://via.placeholder.com/20/1a1a1a/1a1a1a) |
| `--fg` | `#1a1a1a` | ![#1a1a1a](https://via.placeholder.com/20/1a1a1a/1a1a1a) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e2e8f0` | ![#e2e8f0](https://via.placeholder.com/20/e2e8f0/e2e8f0) |
| `--accent` | `#057dbc` | ![#057dbc](https://via.placeholder.com/20/057dbc/057dbc) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `helvetica` |
| Body | `system-ui, sans-serif` |
| Monospace | `text-transform: uppercase` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #1a1a1a;
  --fg: #1a1a1a;
  --muted: #6B6B6B;
  --border: #e2e8f0;
  --accent: #057dbc;
  --font-display: helvetica;
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

Generated from [`wired/DESIGN.md`](../wired/DESIGN.md)
