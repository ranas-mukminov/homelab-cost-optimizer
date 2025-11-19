from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PowerProfile:
    name: str
    base_idle_watts: float
    watts_per_cpu_core: float
    watts_per_gb_ram: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    name: str
    kind: str
    total_cpu: float
    total_memory_gb: float
    power_profile: PowerProfile
    metadata: Dict[str, Any] = field(default_factory=dict)

    def capacity_remaining(self, workloads: List[Workload]) -> Dict[str, float]:
        cpu_used = sum(w.vcpus for w in workloads if w.node == self.name)
        ram_used = sum(w.memory_gb for w in workloads if w.node == self.name)
        return {
            "cpu": max(self.total_cpu - cpu_used, 0.0),
            "memory_gb": max(self.total_memory_gb - ram_used, 0.0),
        }


@dataclass
class Workload:
    name: str
    workload_type: str
    vcpus: float
    memory_gb: float
    utilization_cpu: float
    utilization_memory: float
    node: str
    uptime_hours: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Inventory:
    nodes: List[Node]
    workloads: List[Workload]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [self._node_to_dict(node) for node in self.nodes],
            "workloads": [asdict(workload) for workload in self.workloads],
        }

    @staticmethod
    def _node_to_dict(node: Node) -> Dict[str, Any]:
        node_dict = asdict(node)
        node_dict["power_profile"] = asdict(node.power_profile)
        return node_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Inventory":  # noqa: D401
        nodes = []
        for item in data.get("nodes", []):
            profile_data = item.get("power_profile", {})
            profile = PowerProfile(
                name=profile_data.get("name", "default"),
                base_idle_watts=float(profile_data.get("base_idle_watts", 60)),
                watts_per_cpu_core=float(profile_data.get("watts_per_cpu_core", 10)),
                watts_per_gb_ram=float(profile_data.get("watts_per_gb_ram", 1)),
            )
            nodes.append(
                Node(
                    name=item["name"],
                    kind=item.get("kind", "unknown"),
                    total_cpu=float(item.get("total_cpu", 0)),
                    total_memory_gb=float(item.get("total_memory_gb", 0)),
                    power_profile=profile,
                    metadata=item.get("metadata", {}),
                )
            )
        workloads = [
            Workload(
                name=item["name"],
                workload_type=item.get("workload_type", "vm"),
                vcpus=float(item.get("vcpus", 0)),
                memory_gb=float(item.get("memory_gb", 0)),
                utilization_cpu=float(item.get("utilization_cpu", 0)),
                utilization_memory=float(item.get("utilization_memory", 0)),
                node=item.get("node", ""),
                uptime_hours=float(item.get("uptime_hours", 0)),
                labels=item.get("labels", {}),
            )
            for item in data.get("workloads", [])
        ]
        return cls(nodes=nodes, workloads=workloads)


@dataclass
class ConsolidationMove:
    workload: Workload
    source_node: str
    target_node: str


@dataclass
class ConsolidationPlan:
    moves: List[ConsolidationMove]
    powered_down_nodes: List[str]
    estimated_watts_saved: float
    estimated_monthly_savings: float
    notes: Optional[str] = None


def group_workloads_by_node(workloads: List[Workload]) -> Dict[str, List[Workload]]:
    grouped: Dict[str, List[Workload]] = {}
    for workload in workloads:
        grouped.setdefault(workload.node, []).append(workload)
    return grouped
