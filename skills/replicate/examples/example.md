# Replicate Design System

> Run ML models via API. Clean white canvas, code-forward.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#646464` | ![#646464](https://via.placeholder.com/20/646464/646464) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#dd4425` | ![#dd4425](https://via.placeholder.com/20/dd4425/dd4425) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `rb-freigeist-neue` |
| Body | `basier-square` |
| Monospace | `jetbrains-mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #646464;
  --fg: #000000;
  --muted: #dd4425;
  --border: #E5E5E5;
  --accent: #2F6FEB;
  --font-display: rb-freigeist-neue;
  --font-body: basier-square;
  --font-mono: jetbrains-mono;
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

Generated from [`replicate/DESIGN.md`](../replicate/DESIGN.md)
