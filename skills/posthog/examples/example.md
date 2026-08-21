# PostHog Design System

> Product analytics. Playful hedgehog branding, developer-friendly dark UI.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#f4f4f4` | ![#f4f4f4](https://via.placeholder.com/20/f4f4f4/f4f4f4) |
| `--surface` | `#FFFFFF` | ![#FFFFFF](https://via.placeholder.com/20/FFFFFF/FFFFFF) |
| `--fg` | `#4d4f46` | ![#4d4f46](https://via.placeholder.com/20/4d4f46/4d4f46) |
| `--muted` | `#65675e` | ![#65675e](https://via.placeholder.com/20/65675e/65675e) |
| `--border` | `#b17816` | ![#b17816](https://via.placeholder.com/20/b17816/b17816) |
| `--accent` | `#3b82f6` | ![#3b82f6](https://via.placeholder.com/20/3b82f6/3b82f6) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `Source Code Pro` |
| Body | `IBM Plex Sans Variable` |
| Monospace | `Source Code Pro` |

## CSS Custom Properties

```css
:root {
  --bg: #f4f4f4;
  --surface: #FFFFFF;
  --fg: #4d4f46;
  --muted: #65675e;
  --border: #b17816;
  --accent: #3b82f6;
  --font-display: Source Code Pro;
  --font-body: IBM Plex Sans Variable;
  --font-mono: Source Code Pro;
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

Generated from [`posthog/DESIGN.md`](../posthog/DESIGN.md)
