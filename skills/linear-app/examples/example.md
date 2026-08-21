# Linear Design System

> Project management. Ultra-minimal, precise, purple accent.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#191a1b` | ![#191a1b](https://via.placeholder.com/20/191a1b/191a1b) |
| `--fg` | `#08090a` | ![#08090a](https://via.placeholder.com/20/08090a/08090a) |
| `--muted` | `#d0d6e0` | ![#d0d6e0](https://via.placeholder.com/20/d0d6e0/d0d6e0) |
| `--border` | `#3e3e44` | ![#3e3e44](https://via.placeholder.com/20/3e3e44/3e3e44) |
| `--accent` | `#7170ff` | ![#7170ff](https://via.placeholder.com/20/7170ff/7170ff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Inter Variable` |
| Body | `system-ui, sans-serif` |
| Monospace | `Berkeley Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #191a1b;
  --fg: #08090a;
  --muted: #d0d6e0;
  --border: #3e3e44;
  --accent: #7170ff;
  --font-display: Inter Variable;
  --font-body: system-ui, sans-serif;
  --font-mono: Berkeley Mono;
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

Generated from [`linear-app/DESIGN.md`](../linear-app/DESIGN.md)
