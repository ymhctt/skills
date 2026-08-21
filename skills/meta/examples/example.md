# Meta (Store) Design System

> Tech retail store. Photography-first, binary light/dark surfaces, Meta Blue CTAs.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--surface` | `#F1F4F7` | ![#F1F4F7](https://via.placeholder.com/20/F1F4F7/F1F4F7) |
| `--fg` | `#FF66BF` | ![#FF66BF](https://via.placeholder.com/20/FF66BF/FF66BF) |
| `--muted` | `#465A69` | ![#465A69](https://via.placeholder.com/20/465A69/465A69) |
| `--border` | `#CED0D4` | ![#CED0D4](https://via.placeholder.com/20/CED0D4/CED0D4) |
| `--accent` | `#050505` | ![#050505](https://via.placeholder.com/20/050505/050505) |

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
  --surface: #F1F4F7;
  --fg: #FF66BF;
  --muted: #465A69;
  --border: #CED0D4;
  --accent: #050505;
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

Generated from [`meta/DESIGN.md`](../meta/DESIGN.md)
