# ElevenLabs Design System

> AI voice platform. Dark cinematic UI, audio-waveform aesthetics.

## Color Palette

| Token | Value | Preview |
|-------|-------|---------|
| `--bg` | `#ffffff` | ![#ffffff](https://via.placeholder.com/20/ffffff/ffffff) |
| `--surface` | `#f5f5f5` | ![#f5f5f5](https://via.placeholder.com/20/f5f5f5/f5f5f5) |
| `--fg` | `#000000` | ![#000000](https://via.placeholder.com/20/000000/000000) |
| `--muted` | `#6B6B6B` | ![#6B6B6B](https://via.placeholder.com/20/6B6B6B/6B6B6B) |
| `--border` | `#e5e5e5` | ![#e5e5e5](https://via.placeholder.com/20/e5e5e5/e5e5e5) |
| `--accent` | `#2F6FEB` | ![#2F6FEB](https://via.placeholder.com/20/2F6FEB/2F6FEB) |

## Typography

| Role | Font Family |
|------|-------------|
| Display / Headings | `WaldenburgFH` |
| Body | `Inter` |
| Monospace | `Geist Mono` |

## CSS Custom Properties

```css
:root {
  --bg: #ffffff;
  --surface: #f5f5f5;
  --fg: #000000;
  --muted: #6B6B6B;
  --border: #e5e5e5;
  --accent: #2F6FEB;
  --font-display: WaldenburgFH;
  --font-body: Inter;
  --font-mono: Geist Mono;
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

Generated from [`elevenlabs/DESIGN.md`](../elevenlabs/DESIGN.md)
