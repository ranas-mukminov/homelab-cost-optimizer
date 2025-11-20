from __future__ import annotations

import json
import subprocess
from typing import Callable, List

from ..models import Inventory, Node, PowerProfile, Workload
from .base import BaseCollector


class KubernetesCollector(BaseCollector):
    """Collect node and pod data via kubectl."""

    def __init__(
        self,
        power_profile: PowerProfile,
        context: str | None = None,
        runner: Callable[[List[str]], str] | None = None,
    ) -> None:
        super().__init__(power_profile)
        self.context = context
        self.runner = runner or self._run_command

    def _run_command(self, args: List[str]) -> str:
        process = subprocess.run(args, check=True, capture_output=True, text=True)
        return process.stdout

    def collect(self) -> Inventory:
        nodes_data = self._kubectl(["get", "nodes", "-o", "json"])
        pods_data = self._kubectl(["get", "pods", "-A", "-o", "json"])
        nodes = [self._node_from_item(item) for item in nodes_data.get("items", [])]
        workloads = [self._pod_to_workload(item) for item in pods_data.get("items", [])]
        workloads = [w for w in workloads if w]
        return Inventory(nodes=nodes, workloads=workloads)

    def _kubectl(self, extra_args: List[str]) -> dict:
        args = ["kubectl"]
        if self.context:
            args.extend(["--context", self.context])
        args.extend(extra_args)
        output = self.runner(args)
        return json.loads(output)

    def _node_from_item(self, item: dict) -> Node:
        capacity = item.get("status", {}).get("capacity", {})
        cpu = self._parse_cpu(capacity.get("cpu", "0"))
        memory_gb = self._parse_memory(capacity.get("memory", "0"))
        return Node(
            name=item.get("metadata", {}).get("name", "node"),
            kind="k8s-node",
            total_cpu=cpu,
            total_memory_gb=memory_gb,
            power_profile=self.power_profile,
            metadata={"labels": item.get("metadata", {}).get("labels", {})},
        )

    def _pod_to_workload(self, item: dict) -> Workload | None:
        node_name = item.get("spec", {}).get("nodeName")
        if not node_name:
            return None
        containers = item.get("spec", {}).get("containers", [])
        cpu = sum(
            self._parse_cpu((c.get("resources", {}).get("requests", {}) or {}).get("cpu", "0"))
            for c in containers
        )
        mem = sum(
            self._parse_memory(
                (c.get("resources", {}).get("requests", {}) or {}).get("memory", "0")
            )
            for c in containers
        )
        return Workload(
            name=item.get("metadata", {}).get("name", "pod"),
            workload_type="pod",
            vcpus=cpu,
            memory_gb=mem,
            utilization_cpu=0.0,
            utilization_memory=0.0,
            node=node_name,
            uptime_hours=0.0,
            labels=item.get("metadata", {}).get("labels", {}),
        )

    @staticmethod
    def _parse_cpu(value: str) -> float:
        if value.endswith("m"):
            return float(value[:-1]) / 1000
        return float(value or 0)

    @staticmethod
    def _parse_memory(value: str) -> float:
        value = value or "0"
        suffix_map = {
            "Ki": 1024,
            "Mi": 1024**2,
            "Gi": 1024**3,
        }
        for suffix, factor in suffix_map.items():
            if value.endswith(suffix):
                numeric = float(value[: -len(suffix)])
                return round(numeric * factor / (1024**3), 3)
        return float(value)
