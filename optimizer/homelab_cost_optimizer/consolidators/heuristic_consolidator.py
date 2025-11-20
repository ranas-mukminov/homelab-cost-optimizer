from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..config import ElectricityConfig, ScenarioConfig
from ..models import (
    ConsolidationMove,
    ConsolidationPlan,
    Inventory,
    Node,
    Workload,
    group_workloads_by_node,
)


@dataclass
class NodeUsage:
    cpu: float
    ram: float


class HeuristicConsolidator:
    def __init__(self, scenario: ScenarioConfig, electricity: ElectricityConfig) -> None:
        self.scenario = scenario
        self.electricity = electricity

    def build_plan(self, inventory: Inventory) -> ConsolidationPlan:
        usage = self._node_usage(inventory)
        grouped = group_workloads_by_node(inventory.workloads)
        moves: List[ConsolidationMove] = []
        powered_down: List[str] = []
        watts_saved = 0.0

        for node in inventory.nodes:
            stats = usage.get(node.name, NodeUsage(cpu=0, ram=0))
            if not self._node_is_candidate(node, stats):
                continue
            workloads = list(grouped.get(node.name, []))
            if not workloads:
                continue
            if self._relocate_workloads(node, workloads, inventory.nodes, usage, moves):
                powered_down.append(node.name)
                watts_saved += node.power_profile.base_idle_watts

        monthly_savings = round(watts_saved * 730 / 1000 * self.electricity.effective_price(), 2)
        plan = ConsolidationPlan(
            moves=moves,
            powered_down_nodes=powered_down,
            estimated_watts_saved=round(watts_saved, 2),
            estimated_monthly_savings=monthly_savings,
            notes="Greedy bin-pack heuristic; validate before production changes.",
        )
        return plan

    def _node_usage(self, inventory: Inventory) -> Dict[str, NodeUsage]:
        usage: Dict[str, NodeUsage] = {}
        for node in inventory.nodes:
            usage[node.name] = NodeUsage(cpu=0.0, ram=0.0)
        for workload in inventory.workloads:
            node_usage = usage.setdefault(workload.node, NodeUsage(cpu=0.0, ram=0.0))
            node_usage.cpu += workload.vcpus
            node_usage.ram += workload.memory_gb
        return usage

    def _node_is_candidate(self, node: Node, usage: NodeUsage) -> bool:
        cpu_util = usage.cpu / node.total_cpu if node.total_cpu else 0
        ram_util = usage.ram / node.total_memory_gb if node.total_memory_gb else 0
        return cpu_util < self.scenario.cpu_threshold and ram_util < self.scenario.ram_threshold

    def _relocate_workloads(
        self,
        source_node: Node,
        workloads: List[Workload],
        nodes: List[Node],
        usage: Dict[str, NodeUsage],
        moves: List[ConsolidationMove],
    ) -> bool:
        workloads_sorted = sorted(workloads, key=lambda w: (w.vcpus, w.memory_gb), reverse=True)
        for workload in workloads_sorted:
            destination = self._find_target_node(source_node, workload, nodes, usage)
            if not destination:
                return False
            self._move_workload(workload, source_node, destination, usage, moves)
        return True

    def _find_target_node(
        self,
        source_node: Node,
        workload: Workload,
        nodes: List[Node],
        usage: Dict[str, NodeUsage],
    ) -> Node | None:
        for node in sorted(
            nodes, key=lambda n: usage[n.name].cpu / n.total_cpu if n.total_cpu else 0
        ):
            if node.name == source_node.name:
                continue
            if self._fits(workload, node, usage[node.name]):
                return node
        return None

    def _fits(self, workload: Workload, node: Node, usage: NodeUsage) -> bool:
        projected_cpu = usage.cpu + workload.vcpus
        projected_ram = usage.ram + workload.memory_gb
        if projected_cpu / node.total_cpu > self.scenario.max_node_utilization:
            return False
        if projected_ram / node.total_memory_gb > self.scenario.max_node_utilization:
            return False
        return True

    def _move_workload(
        self,
        workload: Workload,
        source_node: Node,
        destination: Node,
        usage: Dict[str, NodeUsage],
        moves: List[ConsolidationMove],
    ) -> None:
        usage[source_node.name].cpu -= workload.vcpus
        usage[source_node.name].ram -= workload.memory_gb
        usage[destination.name].cpu += workload.vcpus
        usage[destination.name].ram += workload.memory_gb
        moves.append(
            ConsolidationMove(
                workload=workload, source_node=source_node.name, target_node=destination.name
            )
        )
