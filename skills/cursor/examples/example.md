# Cursor Design System

> AI-first code editor. Sleek dark interface, gradient accents.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#f7f7f4` | ![#f7f7f4](https://via.placeholder.com/20/f7f7f4/f7f7f4) |
| `--fg` | `#dfa88f` | ![#dfa88f](https://via.placeholder.com/20/dfa88f/dfa88f) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#26251e` | ![#26251e](https://via.placeholder.com/20/26251e/26251e) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `CursorGothic` |
| Body | `"cswh"` |
| Monospace | `berkeleyMono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #f7f7f4;
  --fg: #dfa88f;
  --muted: #6B6B6B;
  --border: #26251e;
  --accent: #2F6FEB;
  --font-display: CursorGothic;
  --font-body: "cswh";
  --font-mono: berkeleyMono;
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

Generated from [`cursor/DESIGN.md`](../cursor/DESIGN.md)
