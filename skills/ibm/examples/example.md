# IBM Design System

> Enterprise technology. Carbon design system, structured blue palette.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#161616` | ![#161616](https://via.placeholder.com/20/161616/161616) |
| `--surface` | `#161616` | ![#161616](https://via.placeholder.com/20/161616/161616) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#c6c6c6` | ![#c6c6c6](https://via.placeholder.com/20/c6c6c6/c6c6c6) |
| `--border` | `#393939` | ![#393939](https://via.placeholder.com/20/393939/393939) |
| `--accent` | `#f4f4f4` | ![#f4f4f4](https://via.placeholder.com/20/f4f4f4/f4f4f4) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `IBM Plex Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #161616;
  --surface: #161616;
  --fg: #111111;
  --muted: #c6c6c6;
  --border: #393939;
  --accent: #f4f4f4;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: IBM Plex Mono;
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

Generated from [`ibm/DESIGN.md`](../ibm/DESIGN.md)
