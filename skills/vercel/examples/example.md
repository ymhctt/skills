# Vercel Design System

> Frontend deployment. Black and white precision, Geist font.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#171717` | ![#171717](https://via.placeholder.com/20/171717/171717) |
| `--fg` | `#de1d8d` | ![#de1d8d](https://via.placeholder.com/20/de1d8d/de1d8d) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#0a72ef` | ![#0a72ef](https://via.placeholder.com/20/0a72ef/0a72ef) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `"tnum"` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #171717;
  --fg: #de1d8d;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #0a72ef;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: "tnum";
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

Generated from [`vercel/DESIGN.md`](../vercel/DESIGN.md)
