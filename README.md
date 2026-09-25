# 热点宝静态内容仓库

用于验证“固定 UI + 每日 JSON + 静态预渲染”的热点宝 1.0 数据化方案。

## 结构

- `template/baseline.html`：固定 C7 UI / 交互基线
- `data/YYYY-MM-DD.json`：每日一期内容
- `data/latest.json`：最新一期日期
- `data/sectors.json`：板块白名单
- `scripts/build.py`：JSON → 静态 HTML 构建脚本
- `index.html`：最新一期静态页面（自动生成）
- `archive/YYYY-MM-DD.html`：历史静态页面（自动生成）

## 构建

```bash
python scripts/build.py
```

JSON 是内容源，HTML 是预渲染产物；新闻、投研拆解和最终结果在关闭 JavaScript 后仍保留在 HTML 中。

当前阶段已完成数据化基础设施；每日 08:00 自动写入 GitHub 尚未接入。
