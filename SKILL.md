---
name: daily-portfolio-review
description: 太平洋证券主账户 8337 + 副账户 7661 的每日 ETF 投资复盘(2 账户独立分析)。激活场景:(1) 用户说"日复盘"/"看下盘"/"跑下报告"/"今天怎么操作"/"持仓诊断"; (2) 用户提供新持仓截图要更新复盘; (3) 用户问"Mavis 复盘"。自动拉新浪/腾讯实时行情 + 4 指标仪表盘 (MA/RSI/MACD/量能) + DeepSeek 6 段 AI 分析 (持仓诊断/大盘环境/板块产业逻辑/科技政策重大消息/综合分析/心理建设) + 3 色灯 (🟢/🟡/🔴) + 黄色 hl-orange 标色 (代码自动标 ETF/板块名,LLM 标消息判断/分析判断/心理建设) + 传 CDN 给用户。**注:** 持仓数据存在 `portfolio/holdings.json`,5 只 ETF: 159915 创业板 / 588200 科创芯片 / 516650 有色 / 513260 恒生科技 / 159516 半导体设备。**激活口令: "Mavis, 继续投资助理工作"**。
---

# Daily Portfolio Review

## Quick Start

跑主副双账户复盘:

```bash
cd /workspace
python3 review/daily_review.py --account both
```

输出:
- `docs/reports/daily-review-YYYY-MM-DD-main.html`
- `docs/reports/daily-review-YYYY-MM-DD-sub2.html`

跑完手动传 CDN (沙箱 Python 不能直调 MCP):

```python
upload_to_cdn(file_path="/workspace/docs/reports/daily-review-YYYY-MM-DD-main.html")
upload_to_cdn(file_path="/workspace/docs/reports/daily-review-YYYY-MM-DD-sub2.html")
```

## 持仓数据

- 位置: `/workspace/portfolio/holdings.json`
- 2 账户: `main` (太平洋 **8337) + `sub2` (太平洋 **7661)
- 用户提供新截图 → 用 `images_understand` OCR → 更新 holdings.json
- 更新后**记得同步** `/workspace/MEMORY.md` 的基准日

## 6 段 AI 报告结构 (v18 方案 2)

| 段 | 标黄规则 | 谁负责 |
|---|---|---|
| 一、持仓诊断 | ETF 名 + 板块名 | ✅ 代码自动 |
| 二、大盘环境 | 不标 | — |
| 三、板块产业逻辑 | 板块 + ETF 名 | ✅ 代码自动 |
| 四、科技/政策重大消息 | 整条消息 | LLM 输出 (不强求) |
| 五、综合分析 | 重要判断结论 | LLM 输出 (不强求) |
| 六、心理建设 | 整段 | LLM 输出 |

**关键词字典** (`core/report.py` `ETF_KEYWORDS`):
- ETF 代码: 159915 / 588200 / 516650 / 513260 / 159516
- ETF 全名: `159915 创业板ETF易方达` / `588200 科创芯片ETF嘉实` / ...
- 板块名: 半导体 / 有色 / 创业板 / 恒生科技 / 港股科技

## 3 色灯规则 (持仓诊断)

| 灯 | 5 指标健康数 | 例 |
|---|---|---|
| 🟢 健康 | 4-5 个 | 159915 创业板 (现价+36.54%) |
| 🟡 关注 | 2-3 个 | 516650 有色 (中性) |
| 🔴 警惕 | 0-1 个 | 513260 恒生 (浮亏-83%) |

**5 指标:** MA(5/20日) / RSI / MACD / 量能 / 浮盈

## 大盘环境段 (3 大指数 + 涨跌幅 + 成交额)

- 数据源: 新浪 `hq.sinajs.cn/list=sh000001,sz399001,sz399006`
- 涨跌幅: 沙箱算
- 成交额: 新浪行情接口
- **不拉涨跌家数/北向资金** (东财封 IP)
- **不加色**

## 仓位纪律 (v2.0.2 永久规矩)

**8-12 起持仓判断 = 只加真实数据, 不做主观判断。**

❌ 5 件事触发 (加仓/急杀/止损/止盈/趋势走坏)  
❌ 关键位数字 (加仓线/止损位/止盈位/趋势走坏位)  
✅ 只留: 持仓表 + 4 指标仪表盘

**用户主动问操作建议时** → 提醒"按规矩, AI 不出操作建议, 自己定夺"。

## 推送 (去钉钉/去 GitHub)

- 跑完直接 `upload_to_cdn` 给用户链接
- 不推钉钉 (errcode 300001)
- 不推 GitHub Pages (卡 queued 风险)

## 凭据

```
~/.openclaw/.env:
  GITHUB_PAT=ghp_...
  DEEPSEEK_API_KEY=sk-...
```

## 常用命令

```bash
# 跑主账户
python3 review/daily_review.py --account main

# 跑副账户
python3 review/daily_review.py --account sub2

# 跑两个
python3 review/daily_review.py --account both

# 跑指定日期 (--date 需要先 mv data 目录)
python3 review/daily_review.py --account both --date 2026-08-11
```

## 报告后处理 (手动调)

如果 LLM 没标够黄, 或需要重排, 改完 `.md` 后:

```python
import re
from pathlib import Path
md = Path("docs/reports/daily-review-2026-08-12-main.md").read_text()
m = re.search(r"## 🤖 AI 分析(.+?)(?=---)", md, re.DOTALL)
ai_md = "## 🤖 AI 分析" + m.group(1)
from core.report import render_ai_html
ai_html = render_ai_html(ai_md)
html = Path("docs/reports/daily-review-2026-08-12-main.html").read_text()
new_html = re.sub(r'<div class="insight">.*?</div>', ai_html, html, count=1, flags=re.DOTALL)
Path("docs/reports/daily-review-2026-08-12-main.html").write_text(new_html)
```

## 8-12 v18 迭代历史 (备忘)

- v1-v3: 删持仓诊断 + AI 段 3 段
- v4: 仪表盘 + AI 451 字
- v5: 5 段 AI 段 1748 字
- v6: 持仓诊断纯指标 + 风险机会带操作建议表
- v7: "综合分析" 段 5 段 AI 段
- v8: 6 段 AI 段 (删大盘情绪)
- v9: 隐藏 2/3 段
- v10: 综合分析段禁主观词
- v11: 持仓诊断加 3 色灯
- v12: 整段标橙 + CSS 注入
- v13: 加回宏观锚点 (3800/4000/4190)
- v14: 标题 h3 + hl-orange CSS
- v15: 综合分析 3+3 → 2 关键判断
- v16: 砍 4 个不重要标橙 → 留 2 个
- v17: 清理 (删 cdn_uploader.py / render_index / 重复 process_inline)
- v18: 改色橙→黄 + prompt 4/5 段改为"判断" + 方案 2 (代码自动标 ETF/板块名)

## Resources

- `scripts/llm.py` - DeepSeek 调用 + prompt
- `scripts/report.py` - HTML 渲染 + ETF 关键词自动标色
- `scripts/analyze.py` - 持仓分析 (极简, 只算市值/浮盈)
- `scripts/fetch.py` - 新浪/腾讯行情
- `scripts/tech_indicators.py` - 4 指标 (MA/RSI/MACD/量能)
- `scripts/agent_data.py` - 沙箱拉数据
- `scripts/pull_agent_data.py` - 拉数据主流程
- `scripts/industry_news.py` - 行业新闻筛选
- `scripts/daily_review.py` - 主流程入口
