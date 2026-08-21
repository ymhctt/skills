# Webflow Design System

> Visual web builder. Blue-accented, polished marketing site aesthetic.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#222222` | ![#222222](https://via.placeholder.com/20/222222/222222) |
| `--fg` | `#ed52cb` | ![#ed52cb](https://via.placeholder.com/20/ed52cb/ed52cb) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#898989` | ![#898989](https://via.placeholder.com/20/898989/898989) |
| `--accent` | `#146ef5` | ![#146ef5](https://via.placeholder.com/20/146ef5/146ef5) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #FAFAFA;
  --surface: #222222;
  --fg: #ed52cb;
  --muted: #6B6B6B;
  --border: #898989;
  --accent: #146ef5;
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

Generated from [`webflow/DESIGN.md`](../webflow/DESIGN.md)
