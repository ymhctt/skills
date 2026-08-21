# Warm Editorial Design System

> A serif-led magazine aesthetic. Terracotta accent on warm off-white paper —

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#8A817A` | ![#8A817A](https://via.placeholder.com/20/8A817A/8A817A) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#C0512F` | ![#C0512F](https://via.placeholder.com/20/C0512F/C0512F) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `'GT Sectra', 'Times New Roman', serif` |
| Body | `'Söhne', -apple-system, system-ui, sans-serif` |
| Monospace | `'JetBrains Mono', ui-monospace, monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #FAFAFA;
  --surface: #FFFFFF;
  --fg: #111111;
  --muted: #8A817A;
  --border: #E5E5E5;
  --accent: #C0512F;
  --font-display: 'GT Sectra', 'Times New Roman', serif;
  --font-body: 'Söhne', -apple-system, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
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

Generated from [`warm-editorial/DESIGN.md`](../warm-editorial/DESIGN.md)
