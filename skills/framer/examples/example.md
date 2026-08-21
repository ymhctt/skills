# Framer Design System

> Website builder. Bold black and blue, motion-first, design-forward.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#0000ee` | ![#0000ee](https://via.placeholder.com/20/0000ee/0000ee) |
| `--muted` | `#a6a6a6` | ![#a6a6a6](https://via.placeholder.com/20/a6a6a6/a6a6a6) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#0099ff` | ![#0099ff](https://via.placeholder.com/20/0099ff/0099ff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `GT Walsheim Framer Medium` |
| Body | `Inter Variable` |
| Monospace | `Azeret Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #0000ee;
  --muted: #a6a6a6;
  --border: #E5E5E5;
  --accent: #0099ff;
  --font-display: GT Walsheim Framer Medium;
  --font-body: Inter Variable;
  --font-mono: Azeret Mono;
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

Generated from [`framer/DESIGN.md`](../framer/DESIGN.md)
