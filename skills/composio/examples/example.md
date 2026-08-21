# Composio Design System

> Tool integration platform. Modern dark with colorful integration icons.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#0f0f0f` | ![#0f0f0f](https://via.placeholder.com/20/0f0f0f/0f0f0f) |
| `--muted` | `#444444` | ![#444444](https://via.placeholder.com/20/444444/444444) |
| `--border` | `#e0e0e0` | ![#e0e0e0](https://via.placeholder.com/20/e0e0e0/e0e0e0) |
| `--accent` | `#0089ff` | ![#0089ff](https://via.placeholder.com/20/0089ff/0089ff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `uppercase` |
| Body | `system-ui, sans-serif` |
| Monospace | `Menlo` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #FFFFFF;
  --fg: #0f0f0f;
  --muted: #444444;
  --border: #e0e0e0;
  --accent: #0089ff;
  --font-display: uppercase;
  --font-body: system-ui, sans-serif;
  --font-mono: Menlo;
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

Generated from [`composio/DESIGN.md`](../composio/DESIGN.md)
