# Airtable Design System

> Spreadsheet-database hybrid. Colorful, friendly, structured data aesthetic.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#333333` | ![#333333](https://via.placeholder.com/20/333333/333333) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e0e2e6` | ![#e0e2e6](https://via.placeholder.com/20/e0e2e6/e0e2e6) |
| `--accent` | `#1b61c9` | ![#1b61c9](https://via.placeholder.com/20/1b61c9/1b61c9) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Haas Groot Disp` |
| Body | `system-ui, sans-serif` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #333333;
  --fg: #111111;
  --muted: #6B6B6B;
  --border: #e0e2e6;
  --accent: #1b61c9;
  --font-display: Haas Groot Disp;
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

Generated from [`airtable/DESIGN.md`](../airtable/DESIGN.md)
