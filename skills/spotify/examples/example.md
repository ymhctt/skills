# Spotify Design System

> Music streaming. Vibrant green on dark, bold type, album-art-driven.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#181818` | ![#181818](https://via.placeholder.com/20/181818/181818) |
| `--fg` | `#121212` | ![#121212](https://via.placeholder.com/20/121212/121212) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#7c7c7c` | ![#7c7c7c](https://via.placeholder.com/20/7c7c7c/7c7c7c) |
| `--accent` | `#539df5` | ![#539df5](https://via.placeholder.com/20/539df5/539df5) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `system-ui, sans-serif` |
| Body | `SpotifyMixUI` |
| Monospace | `monospace` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #181818;
  --fg: #121212;
  --muted: #6B6B6B;
  --border: #7c7c7c;
  --accent: #539df5;
  --font-display: system-ui, sans-serif;
  --font-body: SpotifyMixUI;
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

Generated from [`spotify/DESIGN.md`](../spotify/DESIGN.md)
