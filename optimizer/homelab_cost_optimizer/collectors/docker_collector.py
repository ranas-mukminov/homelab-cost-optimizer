from __future__ import annotations

import subprocess
from typing import Callable, List

from ..models import Inventory, Node, PowerProfile, Workload
from .base import BaseCollector


class DockerCollector(BaseCollector):
    """Collect container information from Docker CLI."""

    def __init__(
        self,
        power_profile: PowerProfile,
        host_name: str = "docker-host",
        host_cpu: float = 16,
        host_memory_gb: float = 64,
        runner: Callable[[List[str]], str] | None = None,
    ) -> None:
        super().__init__(power_profile)
        self.host_name = host_name
        self.host_cpu = host_cpu
        self.host_memory_gb = host_memory_gb
        self.runner = runner or self._run_command

    def _run_command(self, args: List[str]) -> str:
        process = subprocess.run(args, check=True, capture_output=True, text=True)
        return process.stdout

    def collect(self) -> Inventory:
        stats_output = self.runner(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.Container}},{{.CPUPerc}},{{.MemUsage}}",
            ]
        )
        workloads = [self._parse_stats_line(line) for line in stats_output.splitlines() if line]
        node = Node(
            name=self.host_name,
            kind="docker",
            total_cpu=self.host_cpu,
            total_memory_gb=self.host_memory_gb,
            power_profile=self.power_profile,
            metadata={},
        )
        return Inventory(nodes=[node], workloads=[w for w in workloads if w])

    def _parse_stats_line(self, line: str) -> Workload | None:
        try:
            container_id, cpu_str, mem_str = line.split(",", 2)
        except ValueError:
            return None
        cpu = float(cpu_str.strip().replace("%", "")) / 100
        mem_value = mem_str.split("/")[0].strip()
        mem_gb = self._parse_memory(mem_value)
        return Workload(
            name=container_id,
            workload_type="container",
            vcpus=1.0,
            memory_gb=mem_gb,
            utilization_cpu=cpu,
            utilization_memory=0.0,
            node=self.host_name,
            uptime_hours=0.0,
        )

    @staticmethod
    def _parse_memory(value: str) -> float:
        if value.lower().endswith("gib"):
            return float(value[:-3])
        if value.lower().endswith("mib"):
            return round(float(value[:-3]) / 1024, 3)
        if value.lower().endswith("kib"):
            return round(float(value[:-3]) / (1024 * 1024), 3)
        return float(value)
