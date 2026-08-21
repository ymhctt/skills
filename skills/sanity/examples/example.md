# Sanity Design System

> Headless CMS. Red accent, content-first editorial layout.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#212121` | ![#212121](https://via.placeholder.com/20/212121/212121) |
| `--fg` | `#0b0b0b` | ![#0b0b0b](https://via.placeholder.com/20/0b0b0b/0b0b0b) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#0b0b0b` | ![#0b0b0b](https://via.placeholder.com/20/0b0b0b/0b0b0b) |
| `--accent` | `#0052ef` | ![#0052ef](https://via.placeholder.com/20/0052ef/0052ef) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `waldenburgNormal` |
| Body | `"cv01", "cv11", "cv12", "cv13", "ss07"` |
| Monospace | `text-transform: uppercase` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #212121;
  --fg: #0b0b0b;
  --muted: #6B6B6B;
  --border: #0b0b0b;
  --accent: #0052ef;
  --font-display: waldenburgNormal;
  --font-body: "cv01", "cv11", "cv12", "cv13", "ss07";
  --font-mono: text-transform: uppercase;
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

Generated from [`sanity/DESIGN.md`](../sanity/DESIGN.md)
