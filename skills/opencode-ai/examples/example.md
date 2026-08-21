# OpenCode Design System

> AI coding platform. Developer-centric dark theme.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#FAFAFA` | ![#FAFAFA](https://via.placeholder.com/20/FAFAFA/FAFAFA) |
| `--surface` | `#9a9898` | ![#9a9898](https://via.placeholder.com/20/9a9898/9a9898) |
| `--fg` | `#111111` | ![#111111](https://via.placeholder.com/20/111111/111111) |
| `--muted` | `#6e6e73` | ![#6e6e73](https://via.placeholder.com/20/6e6e73/6e6e73) |
| `--border` | `#9a9898` | ![#9a9898](https://via.placeholder.com/20/9a9898/9a9898) |
| `--accent` | `#007aff` | ![#007aff](https://via.placeholder.com/20/007aff/007aff) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `system-ui, sans-serif` |
| Monospace | `Berkeley Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #FAFAFA;
  --surface: #9a9898;
  --fg: #111111;
  --muted: #6e6e73;
  --border: #9a9898;
  --accent: #007aff;
  --font-display: system-ui, sans-serif;
  --font-body: system-ui, sans-serif;
  --font-mono: Berkeley Mono;
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

Generated from [`opencode-ai/DESIGN.md`](../opencode-ai/DESIGN.md)
