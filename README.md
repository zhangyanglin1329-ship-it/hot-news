# 热点宝静态内容仓库

当前仓库用于验证“固定 UI + 每日 JSON + 静态构建”的 1.0 方案。

## 当前基线

- UI/交互基线：`C7_0925最新内容版_初始化修正版`
- 内容数据：`data/YYYY-MM-DD.json`
- 最新一期指针：`data/latest.json`
- 固定模板：`template/page.html`
- 构建脚本：`scripts/build.py`
- 最新页面：`index.html`
- 历史静态页：`archive/YYYY-MM-DD.html`

当前阶段只完成数据化基础设施，尚未接入每日 08:00 自动写仓库。