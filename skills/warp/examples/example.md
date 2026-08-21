# Warp Design System

> Modern terminal. Dark IDE-like interface, block-based command UI.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#353534` | ![#353534](https://via.placeholder.com/20/353534/353534) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#E5E5E5` | ![#E5E5E5](https://via.placeholder.com/20/E5E5E5/E5E5E5) |
| `--accent` | `#666469` | ![#666469](https://via.placeholder.com/20/666469/666469) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Geist Mono` |
| Body | `Matter Regular` |
| Monospace | `Matter Mono Regular` |

## CSS Custom Properties

```css
:root {
  --bg: #FAFAFA;
  --surface: #353534;
  --fg: #111111;
  --muted: #6B6B6B;
  --border: #E5E5E5;
  --accent: #666469;
  --font-display: Geist Mono;
  --font-body: Matter Regular;
  --font-mono: Matter Mono Regular;
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

Generated from [`warp/DESIGN.md`](../warp/DESIGN.md)
