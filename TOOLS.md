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

## ⏰ 定时任务（微信推送）

| 任务 | 时间 | cron ID | 模式 |
|------|------|---------|------|
| 每日早间汇总 | 7:20 | f83760d8-9fa7-4b39-b0e4-56064ac465fb | announce+isolated |
| 每日早间简报 | 8:00 | 795bfadc | 贵阳天气+国内外各10条热点新闻 | announce+isolated |
| 东西大区周报工统计 | 9:00 | 809faa14-dbce-4a04-8779-676b47f95a29 | announce+isolated |

## ⏰ 定时任务（静默）

| 任务 | 时间 | cron ID | 说明 |
|------|------|---------|------|
| inbound媒体清理 | 每天 2:00 | ce65d49c-6f01-40b5-b33e-3b1153f4f706 | main session |
| MES CLI 自动更新 | 每天 3:00 | ad3dc4bb-b1aa-43aa-9a77-eb2b94839b7a | main session |
| Git 知识库同步 | 每天 7:00 | f193150b-c2c8-47b7-85e6-59ce1b57ed95 | main session |
| 每小时 Memory 提炼 | 每小时 :00 | 14190602-dfc2-4900-80be-0780e830e7c6 | isolated |
| 每周 Memory 归档 | 周一 2:00 | 2a2a6489-b7ec-42cd-a129-6e5635a2cdb9 | isolated |

## 📝 Cron 模式说明

- **announce+isolated**：isolated session 执行完直接推送微信，不依赖主会话
  - 适用：需要推送微信、轻量任务（&lt;60秒）
  - 注意：isolated 有冷启动约60秒，轻量任务可忽略
- **main session**：在主会话中处理，可能被聊天延迟
  - 适用：后台静默任务

---

## 🧹 inbound 媒体文件清理
