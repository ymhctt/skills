# Kraken Design System

> Crypto trading. Purple-accented dark UI, data-dense dashboards.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#686b82` | ![#686b82](https://via.placeholder.com/20/686b82/686b82) |
| `--fg` | `#101114` | ![#101114](https://via.placeholder.com/20/101114/101114) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#7132f5` | ![#7132f5](https://via.placeholder.com/20/7132f5/7132f5) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Kraken-Brand` |
| Body | `Kraken-Product` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #686b82;
  --fg: #101114;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #7132f5;
  --font-display: Kraken-Brand;
  --font-body: Kraken-Product;
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

Generated from [`kraken/DESIGN.md`](../kraken/DESIGN.md)
