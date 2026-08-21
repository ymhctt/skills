# Clay Design System

> Creative agency. Organic shapes, soft gradients, art-directed layout.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#dad4c8` | ![#dad4c8](https://via.placeholder.com/20/dad4c8/dad4c8) |
| `--accent` | `#01418d` | ![#01418d](https://via.placeholder.com/20/01418d/01418d) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `"ss01"` |
| Body | `"ss01"` |
| Monospace | `Space Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #000000;
  --muted: #6B6B6B;
  --border: #dad4c8;
  --accent: #01418d;
  --font-display: "ss01";
  --font-body: "ss01";
  --font-mono: Space Mono;
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

Generated from [`clay/DESIGN.md`](../clay/DESIGN.md)
