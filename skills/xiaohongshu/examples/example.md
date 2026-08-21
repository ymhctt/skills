# Xiaohongshu Design System

> Lifestyle UGC social platform. Singular brand red, generous radius, content-first.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#F5F5F5` | ![#F5F5F5](https://via.placeholder.com/20/F5F5F5/F5F5F5) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#133667` | ![#133667](https://via.placeholder.com/20/133667/133667) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#FF2E4D` | ![#FF2E4D](https://via.placeholder.com/20/FF2E4D/FF2E4D) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `--h3` |
| Body | `--b2-loose` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #F5F5F5;
  --surface: #FFFFFF;
  --fg: #133667;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #FF2E4D;
  --font-display: --h3;
  --font-body: --b2-loose;
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

Generated from [`xiaohongshu/DESIGN.md`](../xiaohongshu/DESIGN.md)
