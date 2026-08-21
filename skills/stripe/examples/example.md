# Stripe Design System

> Payment infrastructure. Signature purple gradients, weight-300 elegance.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#64748d` | ![#64748d](https://via.placeholder.com/20/64748d/64748d) |
| `--border` | `#e5edf5` | ![#e5edf5](https://via.placeholder.com/20/e5edf5/e5edf5) |
| `--accent` | `#533afd` | ![#533afd](https://via.placeholder.com/20/533afd/533afd) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `sohne-var` |
| Body | `"ss01"` |
| Monospace | `SourceCodePro` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #111111;
  --muted: #64748d;
  --border: #e5edf5;
  --accent: #533afd;
  --font-display: sohne-var;
  --font-body: "ss01";
  --font-mono: SourceCodePro;
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

Generated from [`stripe/DESIGN.md`](../stripe/DESIGN.md)
