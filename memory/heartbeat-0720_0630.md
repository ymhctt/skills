# heartbeat-0720_0630

## [07:20] morning_brief_attempt | 早间汇总推送异常

- 07:20 CST 早间汇总 cron 触发
- 微信通道 sendMessage ret=-2（连发 2 次均失败，包括 1 次最小化 test），属基础设施层异常
- 06-29 历史：07:00 微信通道自测成功（msgId 1782687664742-6b20846d），09h 推送 OK
- 当前策略：微信通道异常 → 凭据会话 plain-text 自动回传兜底，不重复推送避免打扰
- 08:00 早间简报 cron（in 40m）若届时通道仍未恢复，将同样以 plain-text 兜底
- 已记录到 memory/cron.log
