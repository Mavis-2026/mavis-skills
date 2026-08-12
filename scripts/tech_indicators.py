"""
core/tech_indicators.py - 4 大技术指标计算
- MA (5/20/60)
- RSI (14)
- MACD (12,26,9)
- 量能比 (当日量 / 5 日均量)
全 4 个指标 = 机器能算, 零主观
"""
from typing import Dict, List, Optional


def calc_ma(closes: List[float], n: int) -> Optional[float]:
    """简单移动平均"""
    if len(closes) < n:
        return None
    return round(sum(closes[-n:]) / n, 4)


def calc_rsi(closes: List[float], n: int = 14) -> Optional[float]:
    """RSI 相对强弱指数 (0-100, <30 超卖, >70 超买)"""
    if len(closes) < n + 1:
        return None
    gains = []
    losses = []
    for i in range(-n, 0):
        diff = closes[i] - closes[i - 1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(-diff)
    avg_gain = sum(gains) / n if gains else 0
    avg_loss = sum(losses) / n if losses else 0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calc_macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """
    MACD 指标
    返回: {
        "dif": 快线 - 慢线 (EMA),
        "dea": 信号线 (EMA of DIF),
        "macd": 柱状 = (DIF - DEA) * 2,
        "trend": "红柱变长" / "红柱变短" / "绿柱变长" / "绿柱变短" / "持平"
    }
    """
    if len(closes) < slow + signal:
        return {"dif": None, "dea": None, "macd": None, "trend": "数据不足"}

    def ema(data: List[float], n: int) -> List[float]:
        result = [data[0]]
        k = 2 / (n + 1)
        for price in data[1:]:
            result.append(price * k + result[-1] * (1 - k))
        return result

    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    dif_series = [f - s for f, s in zip(ema_fast, ema_slow)]
    dea_series = ema(dif_series, signal)
    macd_series = [(d - dea) * 2 for d, dea in zip(dif_series, dea_series)]

    dif = round(dif_series[-1], 4)
    dea = round(dea_series[-1], 4)
    macd = round(macd_series[-1], 4)

    # 趋势判断
    if len(macd_series) < 2:
        trend = "持平"
    else:
        prev = macd_series[-2]
        curr = macd_series[-1]
        if curr > 0 and prev > 0:
            trend = "红柱变长" if curr > prev else "红柱变短"
        elif curr < 0 and prev < 0:
            trend = "绿柱变长" if abs(curr) > abs(prev) else "绿柱变短"
        elif curr > 0 and prev <= 0:
            trend = "金叉(转红)"
        elif curr < 0 and prev >= 0:
            trend = "死叉(转绿)"
        else:
            trend = "持平"

    return {"dif": dif, "dea": dea, "macd": macd, "trend": trend}


def calc_volume_ratio(volumes: List[float]) -> Optional[float]:
    """量能比 = 当日量 / 5 日均量"""
    if len(volumes) < 6:
        return None
    today = volumes[-1]
    avg_5 = sum(volumes[-6:-1]) / 5
    if avg_5 == 0:
        return None
    return round(today / avg_5, 2)


def calc_tech_indicators(klines: List) -> Dict:
    """
    输入腾讯 K 线格式: [date, open, close, high, low, volume]
    返回 4 大指标仪表盘
    """
    if not klines or len(klines) < 30:
        return {"error": "K线数据不足"}

    closes = [float(k[2]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    current = closes[-1]

    ma5 = calc_ma(closes, 5)
    ma20 = calc_ma(closes, 20)
    ma60 = calc_ma(closes, 60)
    rsi = calc_rsi(closes, 14)
    macd_data = calc_macd(closes)
    vol_ratio = calc_volume_ratio(volumes)

    # 信号判断 (布尔)
    above_ma5 = current > ma5 if ma5 else None
    above_ma20 = current > ma20 if ma20 else None
    above_ma60 = current > ma60 if ma60 else None
    rsi_oversold = rsi < 30 if rsi is not None else None
    rsi_overbought = rsi > 70 if rsi is not None else None
    macd_bull = macd_data["macd"] is not None and macd_data["macd"] > 0
    vol_shrink = vol_ratio is not None and vol_ratio < 0.7
    vol_surge = vol_ratio is not None and vol_ratio > 1.5

    # 4 指标 评分
    score = 0
    if above_ma5:
        score += 1
    if rsi_oversold:
        score += 1
    if macd_data["trend"] in ["金叉(转红)", "红柱变长"]:
        score += 1
    if vol_shrink and current < ma5:  # 缩量止跌
        score += 1

    return {
        "current": round(current, 4),
        "ma5": ma5,
        "ma20": ma20,
        "ma60": ma60,
        "above_ma5": above_ma5,
        "above_ma20": above_ma20,
        "above_ma60": above_ma60,
        "rsi": rsi,
        "rsi_oversold": rsi_oversold,
        "rsi_overbought": rsi_overbought,
        "macd": macd_data,
        "macd_bull": macd_bull,
        "vol_ratio": vol_ratio,
        "vol_shrink": vol_shrink,
        "vol_surge": vol_surge,
        "score": score,
        "max_score": 4,
    }


def render_tech_dashboard(code: str, name: str, data: Dict) -> str:
    """渲染 4 指标仪表盘为 Markdown 表格"""
    if "error" in data:
        return f"**{code} {name}**: 数据不足"

    def status(b):
        return "✅" if b else "❌"

    current = data["current"]
    ma5 = data["ma5"]
    ma20 = data["ma20"]
    ma60 = data["ma60"]
    rsi = data["rsi"]
    macd = data["macd"]
    vol_ratio = data["vol_ratio"]
    score = data["score"]

    lines = [
        f"**{code} {name}** | 现价 {current}",
        "",
        "| 指标 | 数值 | 状态 |",
        "|---|---|---|",
        f"| 5 日线 | {ma5} | 现价 {'上方 ✅' if data['above_ma5'] else '下方 ❌'} |",
        f"| 20 日线 | {ma20} | 现价 {'上方 ✅' if data['above_ma20'] else '下方 ❌'} |",
        f"| 60 日线 | {ma60} | 现价 {'上方 ✅' if data['above_ma60'] else '下方 ❌'} |",
        f"| RSI(14) | {rsi} | {'超卖 ✅' if data['rsi_oversold'] else '超买 ⚠️' if data['rsi_overbought'] else '中性'} |",
        f"| MACD | {macd['macd']} | {macd['trend']} |",
        f"| 量能比 | {vol_ratio} | {'缩量 ✅' if data['vol_shrink'] else '放量 ⚠️' if data['vol_surge'] else '正常'} |",
        "",
        f"📊 **4 指标 {score}/4 满足**",
    ]
    return "\n".join(lines)
