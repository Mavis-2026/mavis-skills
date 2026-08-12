"""
core/industry_news.py - 科技/政策重大新闻筛选 (8-12 加)
- 接收外部传入的新闻列表 (由 daily_review.py 通过 MCP 工具拉)
- 筛科技/政策类
- 满足重大性 = 进报告
- 没有重大新闻 = 返回空
"""
import re
from typing import List, Dict, Optional

# 关键词分类
KEYWORDS = {
    "半导体": ["半导体", "芯片", "集成电路", "晶圆", "中芯国际", "寒武纪", "摩尔线程", "国产替代", "光刻机", "大基金", "GPU", "HBM", "存储"],
    "科技": ["6G", "AI", "人工智能", "量子", "卫星", "大模型", "机器人", "具身智能"],
    "政策": ["国务院", "财政部", "央行", "证监会", "发改委", "工信部", "出口管制", "制裁", "实体清单"],
    "有色": ["铜", "铝", "黄金", "有色金属", "稀土", "锂", "镍", "钨"],
    "港股": ["港股", "恒生", "中概股", "VIE", "港股科技"],
    "创业板": ["创业板", "新能源", "宁德时代", "光伏", "储能", "锂电池"],
}

# 重大性判定标准
MAJOR_KEYWORDS = [
    "国务院", "央行", "财政部", "证监会", "发改委", "工信部", "商务部",
    "出口管制", "制裁", "实体清单", "限制",
    "涨价", "缺货", "短缺", "缺口", "产能", "扩产", "订单",
    "净利润", "营收", "同比", "环比", "业绩", "财报",
    "回购", "增持", "减持", "定增", "IPO", "上市",
    "国家", "中央", "规划", "五年",
]

# 排除词 (一般消息不进)
IGNORE_KEYWORDS = [
    "广告", "营销", "促销", "直播", "网红", "明星", "娱乐",
    "涨停揭秘", "盘中", "异动", "龙虎榜", "换手率", "技术分析",
]


def classify_news(title: str) -> Optional[str]:
    """分类新闻属于哪个板块, 没匹配返回 None"""
    for category, words in KEYWORDS.items():
        for word in words:
            if word in title:
                return category
    return None


def is_major(title: str) -> bool:
    """是否重大新闻"""
    for ig in IGNORE_KEYWORDS:
        if ig in title:
            return False
    for mk in MAJOR_KEYWORDS:
        if mk in title:
            return True
    return False


def filter_news(raw_news: List[Dict]) -> List[Dict]:
    """
    筛选传入的新闻列表
    raw_news: [{title, source, link}, ...] (任意来源,MCP/手动/沙箱)
    返回: [{title, category, source, link}, ...] (筛后按分类)
    """
    all_results = []
    for r in raw_news:
        title = r.get("title", "")
        if not title or len(title) < 10:
            continue
        category = classify_news(title)
        if not category:
            continue
        if not is_major(title):
            continue
        all_results.append({
            "title": title,
            "category": category,
            "source": r.get("source", ""),
            "link": r.get("link", ""),
        })

    # 去重
    seen = set()
    unique = []
    for r in all_results:
        key = r["title"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def render_industry_news_md(news: List[Dict]) -> str:
    """
    渲染重大新闻为 Markdown
    没重大新闻 = 返回空字符串 (不显示这 1 段)
    """
    if not news:
        return ""

    lines = ["", "## 📰 科技/政策重大消息", ""]

    by_cat = {}
    for n in news:
        by_cat.setdefault(n["category"], []).append(n)

    cat_order = ["半导体", "科技", "政策", "有色", "港股", "创业板"]
    for cat in cat_order:
        if cat not in by_cat:
            continue
        lines.append(f"**{cat}**：")
        for n in by_cat[cat][:3]:
            lines.append(f"- {n['title'][:80]}")
        lines.append("")

    return "\n".join(lines)
