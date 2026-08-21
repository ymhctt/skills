# Discord Design System

> Voice / chat platform. Deep blurple, dark-first surfaces, playful accent moments.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#00a8fc` | ![#00a8fc](https://via.placeholder.com/20/00a8fc/00a8fc) |
| `--muted` | `#2b2d31` | ![#2b2d31](https://via.placeholder.com/20/2b2d31/2b2d31) |
| `--border` | `#3f4147` | ![#3f4147](https://via.placeholder.com/20/3f4147/3f4147) |
| `--accent` | `#313338` | ![#313338](https://via.placeholder.com/20/313338/313338) |

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
  --surface: #FFFFFF;
  --fg: #00a8fc;
  --muted: #2b2d31;
  --border: #3f4147;
  --accent: #313338;
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

Generated from [`discord/DESIGN.md`](../discord/DESIGN.md)
