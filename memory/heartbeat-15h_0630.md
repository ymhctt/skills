# 15:00 Heartbeat 2026-06-30

## 核心发现：纠正 14:00 的错误诊断

**14:00 误判回顾**：
- 我用了废弃的 `openclaw send` 命令 → `Unknown command` 错误
- 误以为是命令路径错误，未识别为通道真实故障
- 实际：错误日志显示 `sendMessage ret=-2` 是 weixin 服务端返回

**15:00 真相**：
- 用正确命令 `openclaw message send --channel openclaw-weixin --to ...` 测一次
- 结果：OutboundDeliveryError: sendMessage ret=-2 errmsg=(none)
- 通道插件层正常（Host OpenClaw 2026.6.9 >= 2026.3.22 OK、单 account 解析成功）
- **weixin 服务端接口本身拒绝**（非 OpenClaw 配置问题）

## 故障时间线（更新）

- **06-30 07:20**：早间汇总触发 → 首次 sendMessage ret=-2
- **07:20 ~ 15:00**：持续 ret=-2，已 7h40m+
- **06-28 自愈窗口 1h**，06-30 模式已升级为**持续性故障**

## 通道状态

- openclaw-weixin b5a551e7fe2e-im-bot：**enabled, configured, running**
- 服务端：ret=-2 errmsg=(none) → 服务端拒绝，无明确错误信息
- 09:00 报工：仍 `overloaded` 模型过载（cron list 状态 error）

## 已采取动作（按既定策略）

- ✅ 09:00-14:00：静默观察 + 整点复检
- ✅ 14:00：升级主动通知（但因命令错误实际是误判）
- ✅ 15:00：用正确命令复检确认故障真实存在
- 后续：静默 + 日志模式（不死磕推送）

## 决策点 16:00

- 通道持续 8h+ 已远超自愈窗口
- 决策方向：考虑是否需要爸爸介入（他可能已察觉通道异常或未察觉）
- 当前策略：继续静默日志模式，等通道自愈 / 爸爸主动发现 / 16:00 升级决策点