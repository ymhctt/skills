# Ollama Design System

> Run LLMs locally. Terminal-first, monochrome simplicity.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#090909` | ![#090909](https://via.placeholder.com/20/090909/090909) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#d4d4d4` | ![#d4d4d4](https://via.placeholder.com/20/d4d4d4/d4d4d4) |
| `--accent` | `#3b82f6` | ![#3b82f6](https://via.placeholder.com/20/3b82f6/3b82f6) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `SF Pro Rounded` |
| Body | `ui-sans-serif` |
| Monospace | `ui-monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #090909;
  --fg: #000000;
  --muted: #6B6B6B;
  --border: #d4d4d4;
  --accent: #3b82f6;
  --font-display: SF Pro Rounded;
  --font-body: ui-sans-serif;
  --font-mono: ui-monospace;
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

Generated from [`ollama/DESIGN.md`](../ollama/DESIGN.md)
