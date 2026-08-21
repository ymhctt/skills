# HashiCorp Design System

> Infrastructure automation. Enterprise-clean, black and white.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#efeff1` | ![#efeff1](https://via.placeholder.com/20/efeff1/efeff1) |
| `--surface` | `#f1f2f3` | ![#f1f2f3](https://via.placeholder.com/20/f1f2f3/f1f2f3) |
| `--fg` | `#2264d6` | ![#2264d6](https://via.placeholder.com/20/2264d6/2264d6) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#911ced` | ![#911ced](https://via.placeholder.com/20/911ced/911ced) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `"kern"` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #efeff1;
  --surface: #f1f2f3;
  --fg: #2264d6;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #911ced;
  --font-display: "kern";
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

Generated from [`hashicorp/DESIGN.md`](../hashicorp/DESIGN.md)
