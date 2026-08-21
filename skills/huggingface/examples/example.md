# Hugging Face Design System

> ML community hub. Sunny yellow accent, monospace identity, cheerful and dense.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#0d1117` | ![#0d1117](https://via.placeholder.com/20/0d1117/0d1117) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e5e7eb` | ![#e5e7eb](https://via.placeholder.com/20/e5e7eb/e5e7eb) |
| `--accent` | `#2563eb` | ![#2563eb](https://via.placeholder.com/20/2563eb/2563eb) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `IBM Plex Mono` |
| Body | `Source Sans Pro` |
| Monospace | `model_id` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #0d1117;
  --muted: #6B6B6B;
  --border: #e5e7eb;
  --accent: #2563eb;
  --font-display: IBM Plex Mono;
  --font-body: Source Sans Pro;
  --font-mono: model_id;
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

Generated from [`huggingface/DESIGN.md`](../huggingface/DESIGN.md)
