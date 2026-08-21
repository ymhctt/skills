# Cohere Design System

> Enterprise AI platform. Vibrant gradients, data-rich dashboard aesthetic.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#f2f2f2` | ![#f2f2f2](https://via.placeholder.com/20/f2f2f2/f2f2f2) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#93939f` | ![#93939f](https://via.placeholder.com/20/93939f/93939f) |
| `--border` | `#d9d9dd` | ![#d9d9dd](https://via.placeholder.com/20/d9d9dd/d9d9dd) |
| `--accent` | `#1863dc` | ![#1863dc](https://via.placeholder.com/20/1863dc/1863dc) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `CohereText` |
| Body | `Unica77 Cohere Web` |
| Monospace | `CohereMono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #f2f2f2;
  --fg: #000000;
  --muted: #93939f;
  --border: #d9d9dd;
  --accent: #1863dc;
  --font-display: CohereText;
  --font-body: Unica77 Cohere Web;
  --font-mono: CohereMono;
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

Generated from [`cohere/DESIGN.md`](../cohere/DESIGN.md)
