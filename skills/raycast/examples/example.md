# Raycast Design System

> Productivity launcher. Sleek dark chrome, vibrant gradient accents.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#101111` | ![#101111](https://via.placeholder.com/20/101111/101111) |
| `--fg` | `#07080a` | ![#07080a](https://via.placeholder.com/20/07080a/07080a) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#252829` | ![#252829](https://via.placeholder.com/20/252829/252829) |
| `--accent` | `#55b3ff` | ![#55b3ff](https://via.placeholder.com/20/55b3ff/55b3ff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `calt` |
| Body | `system-ui, sans-serif` |
| Monospace | `GeistMono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #101111;
  --fg: #07080a;
  --muted: #6B6B6B;
  --border: #252829;
  --accent: #55b3ff;
  --font-display: calt;
  --font-body: system-ui, sans-serif;
  --font-mono: GeistMono;
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

Generated from [`raycast/DESIGN.md`](../raycast/DESIGN.md)
