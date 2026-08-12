"""
core/analyze.py - 持仓基础数据计算 (8-12 改: 极简,只算真实数据)
- 删关键位/急杀/止损/止盈/趋势走坏/估值分位
- 只算: 成本/股数/市值/浮盈浮亏
- 5 件事触发判断 = 删
"""
from typing import Dict, List, Optional


def calc_position_metrics(position: Dict, current_price: float, open_price: float = None,
                          valuation_percentile: float = None) -> Dict:
    """
    计算单只持仓的指标 (8-12 改: 只留真实数据)
    """
    cost = position["cost"]
    shares = position["shares"]
    market_value = current_price * shares
    cost_value = cost * shares
    profit = market_value - cost_value
    profit_pct = (profit / cost_value * 100) if cost_value > 0 else 0

    return {
        "code": position["code"],
        "name": position["name"],
        "shares": shares,
        "cost": cost,
        "current_price": current_price,
        "market_value": round(market_value, 2),
        "cost_value": round(cost_value, 2),
        "profit": round(profit, 2),
        "profit_pct": round(profit_pct, 2),
    }


def get_all_signals(positions: List[Dict], index_data: Dict) -> Dict:
    """
    8-12 改: 5 件事触发删除, 返回空信号
    """
    return {
        "position_signals": [],
        "market_signals": [],
        "triggered_count": 0,
    }


def make_decision_summary(all_signals: Dict) -> str:
    """
    8-12 改: 不再给主观决策, 返回空字符串
    """
    return ""
