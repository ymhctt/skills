# GitHub Design System

> Code-forward platform. Functional density, blue-on-white precision, Primer foundations.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#161b22` | ![#161b22](https://via.placeholder.com/20/161b22/161b22) |
| `--fg` | `#bf3989` | ![#bf3989](https://via.placeholder.com/20/bf3989/bf3989) |
| `--muted` | `#656d76` | ![#656d76](https://via.placeholder.com/20/656d76/656d76) |
| `--border` | `#d0d7de` | ![#d0d7de](https://via.placeholder.com/20/d0d7de/d0d7de) |
| `--accent` | `#ddf4ff` | ![#ddf4ff](https://via.placeholder.com/20/ddf4ff/ddf4ff) |

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
  --surface: #161b22;
  --fg: #bf3989;
  --muted: #656d76;
  --border: #d0d7de;
  --accent: #ddf4ff;
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

Generated from [`github/DESIGN.md`](../github/DESIGN.md)
