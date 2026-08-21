# Resend Design System

> Email API. Minimal dark theme, monospace accents.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#464a4d` | ![#464a4d](https://via.placeholder.com/20/464a4d/464a4d) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#fcfdff` | ![#fcfdff](https://via.placeholder.com/20/fcfdff/fcfdff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `"ss01", "ss04", "ss11"` |
| Body | `inter` |
| Monospace | `commitMono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #464a4d;
  --fg: #000000;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #fcfdff;
  --font-display: "ss01", "ss04", "ss11";
  --font-body: inter;
  --font-mono: commitMono;
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

Generated from [`resend/DESIGN.md`](../resend/DESIGN.md)
