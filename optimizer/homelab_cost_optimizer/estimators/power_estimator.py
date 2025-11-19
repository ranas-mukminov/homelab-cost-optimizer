from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..models import Inventory, Node, Workload


@dataclass
class NodePowerUsage:
    node: Node
    watts: float


@dataclass
class PowerReport:
    per_node: List[NodePowerUsage]

    @property
    def total_watts(self) -> float:
        return round(sum(item.watts for item in self.per_node), 2)


def estimate_node_power(node: Node, workloads: List[Workload]) -> NodePowerUsage:
    node_workloads = [w for w in workloads if w.node == node.name]
    total_cpu = sum(w.vcpus * max(w.utilization_cpu, 0.1) for w in node_workloads)
    total_ram = sum(w.memory_gb * max(w.utilization_memory, 0.1) for w in node_workloads)
    profile = node.power_profile
    watts = profile.base_idle_watts + profile.watts_per_cpu_core * total_cpu + profile.watts_per_gb_ram * total_ram
    return NodePowerUsage(node=node, watts=round(watts, 2))


def build_power_report(inventory: Inventory) -> PowerReport:
    per_node = [estimate_node_power(node, inventory.workloads) for node in inventory.nodes]
    return PowerReport(per_node=per_node)
