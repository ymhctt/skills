# Binance.US Design System

> Crypto exchange. Bold yellow accent on monochrome, trading-floor urgency.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--surface` | `#2B2F36` | ![#2B2F36](https://via.placeholder.com/20/2B2F36/2B2F36) |
| `--fg` | `#1E2026` | ![#1E2026](https://via.placeholder.com/20/1E2026/1E2026) |
| `--muted` | `#32313A` | ![#32313A](https://via.placeholder.com/20/32313A/32313A) |
| `--border` | `#E6E8EA` | ![#E6E8EA](https://via.placeholder.com/20/E6E8EA/E6E8EA) |
| `--accent` | `#1E2026` | ![#1E2026](https://via.placeholder.com/20/1E2026/1E2026) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #FFFFFF;
  --surface: #2B2F36;
  --fg: #1E2026;
  --muted: #32313A;
  --border: #E6E8EA;
  --accent: #1E2026;
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

Generated from [`binance/DESIGN.md`](../binance/DESIGN.md)
