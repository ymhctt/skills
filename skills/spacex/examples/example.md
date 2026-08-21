# SpaceX Design System

> Space technology. Stark black and white, full-bleed imagery, futuristic.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#f0f0fa` | ![#f0f0fa](https://via.placeholder.com/20/f0f0fa/f0f0fa) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `text-transform: uppercase` |
| Body | `D-DIN` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #f0f0fa;
  --surface: #FFFFFF;
  --fg: #000000;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #2F6FEB;
  --font-display: text-transform: uppercase;
  --font-body: D-DIN;
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

Generated from [`spacex/DESIGN.md`](../spacex/DESIGN.md)
