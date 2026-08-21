# Cisco Design System

> Enterprise infrastructure brand. Dark trust surfaces, Cisco Blue signal, technical clarity.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#39393b` | ![#39393b](https://via.placeholder.com/20/39393b/39393b) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#58585b` | ![#58585b](https://via.placeholder.com/20/58585b/58585b) |
| `--accent` | `#1b2530` | ![#1b2530](https://via.placeholder.com/20/1b2530/1b2530) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `CiscoSansTT` |
| Body | `CiscoSansTT` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #39393b;
  --fg: #111111;
  --muted: #6B6B6B;
  --border: #58585b;
  --accent: #1b2530;
  --font-display: CiscoSansTT;
  --font-body: CiscoSansTT;
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

Generated from [`cisco/DESIGN.md`](../cisco/DESIGN.md)
