# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## 🧹 inbound 媒体文件清理

- 每天凌晨 2:00 自动执行
- 保留最近 1 天的文件
- cron ID: ce65d49c-6f01-40b5-b33e-3b1153f4f706
- **MES CLI + Skill 自动更新**：每天凌晨 3:00
  - mes update（CLI）
  - git pull origin main（skill）
  - cron ID: b5740ba4-616e-45e1-98d9-8623008c5511
- 日志: /root/.openclaw/media/inbound/cleanup.log

---

Add whatever helps you do your job. This is your cheat sheet.
