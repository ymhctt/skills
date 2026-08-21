# Miro Design System

> Visual collaboration. Bright yellow accent, infinite canvas aesthetic.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#fde0f0` | ![#fde0f0](https://via.placeholder.com/20/fde0f0/fde0f0) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#c7cad5` | ![#c7cad5](https://via.placeholder.com/20/c7cad5/c7cad5) |
| `--accent` | `#5b76fe` | ![#5b76fe](https://via.placeholder.com/20/5b76fe/5b76fe) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Roobert PRO SemiBold` |
| Body | `Noto Sans` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #fde0f0;
  --muted: #6B6B6B;
  --border: #c7cad5;
  --accent: #5b76fe;
  --font-display: Roobert PRO SemiBold;
  --font-body: Noto Sans;
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

Generated from [`miro/DESIGN.md`](../miro/DESIGN.md)
