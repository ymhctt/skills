# Mintlify Design System

> Documentation platform. Clean, green-accented, reading-optimized.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#0d0d0d` | ![#0d0d0d](https://via.placeholder.com/20/0d0d0d/0d0d0d) |
| `--fg` | `#0d0d0d` | ![#0d0d0d](https://via.placeholder.com/20/0d0d0d/0d0d0d) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#18E299` | ![#18E299](https://via.placeholder.com/20/18E299/18E299) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `text-transform: uppercase` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #0d0d0d;
  --fg: #0d0d0d;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #18E299;
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

Generated from [`mintlify/DESIGN.md`](../mintlify/DESIGN.md)
