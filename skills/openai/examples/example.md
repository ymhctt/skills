# OpenAI Design System

> Calm, near-monochrome system anchored in deep teal-black with generous white space and editorial typography.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#3c3c3c` | ![#3c3c3c](https://via.placeholder.com/20/3c3c3c/3c3c3c) |
| `--fg` | `#0d0d0d` | ![#0d0d0d](https://via.placeholder.com/20/0d0d0d/0d0d0d) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e5e5e5` | ![#e5e5e5](https://via.placeholder.com/20/e5e5e5/e5e5e5) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Signifier` |
| Body | `Söhne` |
| Monospace | `Söhne Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #3c3c3c;
  --fg: #0d0d0d;
  --muted: #6B6B6B;
  --border: #e5e5e5;
  --accent: #2F6FEB;
  --font-display: Signifier;
  --font-body: Söhne;
  --font-mono: Söhne Mono;
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

Generated from [`openai/DESIGN.md`](../openai/DESIGN.md)
