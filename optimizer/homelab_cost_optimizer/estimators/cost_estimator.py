from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..config import ElectricityConfig
from .power_estimator import PowerReport


@dataclass
class CostBreakdown:
    node: str
    kwh_month: float
    monthly_cost: float


@dataclass
class CostReport:
    currency: str
    per_node: List[CostBreakdown]

    @property
    def total_monthly_cost(self) -> float:
        return round(sum(item.monthly_cost for item in self.per_node), 2)


def estimate_cost(power_report: PowerReport, config: ElectricityConfig, monthly_hours: float = 730) -> CostReport:
    price = config.effective_price()
    per_node = []
    for entry in power_report.per_node:
        kwh = round(entry.watts * monthly_hours / 1000, 2)
        cost = round(kwh * price, 2)
        per_node.append(CostBreakdown(node=entry.node.name, kwh_month=kwh, monthly_cost=cost))
    return CostReport(currency=config.currency, per_node=per_node)
