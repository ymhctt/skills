# Neutral Modern Design System

> A clean, product-oriented default. Use when the brief doesn't call for a

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `'Inter', -apple-system, system-ui, sans-serif` |
| Body | `'Inter', -apple-system, system-ui, sans-serif` |
| Monospace | `ui-monospace, 'JetBrains Mono', monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #FAFAFA;
  --surface: #FFFFFF;
  --fg: #111111;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #2F6FEB;
  --font-display: 'Inter', -apple-system, system-ui, sans-serif;
  --font-body: 'Inter', -apple-system, system-ui, sans-serif;
  --font-mono: ui-monospace, 'JetBrains Mono', monospace;
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

Generated from [`default/DESIGN.md`](../default/DESIGN.md)
