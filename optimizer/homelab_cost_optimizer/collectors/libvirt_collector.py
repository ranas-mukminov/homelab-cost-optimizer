from __future__ import annotations

import re
import subprocess
from typing import Callable, List

from ..models import Inventory, Node, PowerProfile, Workload
from .base import BaseCollector


class LibvirtCollector(BaseCollector):
    """Collect VM information via the `virsh` CLI."""

    def __init__(
        self,
        power_profile: PowerProfile,
        uri: str = "qemu:///system",
        host_name: str = "libvirt-host",
        host_cpu: float = 32,
        host_memory_gb: float = 128,
        runner: Callable[[List[str]], str] | None = None,
    ) -> None:
        super().__init__(power_profile)
        self.uri = uri
        self.host_name = host_name
        self.host_cpu = host_cpu
        self.host_memory_gb = host_memory_gb
        self.runner = runner or self._run_command

    def _run_command(self, args: List[str]) -> str:
        process = subprocess.run(args, check=True, capture_output=True, text=True)
        return process.stdout

    def collect(self) -> Inventory:
        domains = self._parse_list()
        workloads = [self._dominfo_to_workload(name) for name in domains]
        node = Node(
            name=self.host_name,
            kind="hypervisor",
            total_cpu=self.host_cpu,
            total_memory_gb=self.host_memory_gb,
            power_profile=self.power_profile,
            metadata={"uri": self.uri},
        )
        return Inventory(nodes=[node], workloads=workloads)

    def _parse_list(self) -> List[str]:
        args = ["virsh", "-c", self.uri, "list", "--all"]
        output = self.runner(args)
        domains: List[str] = []
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("Id"):
                continue
            if all(ch == "-" for ch in stripped):
                continue
            parts = stripped.split()
            if len(parts) >= 2:
                domains.append(parts[1])
        return domains

    def _dominfo_to_workload(self, domain: str) -> Workload:
        args = ["virsh", "-c", self.uri, "dominfo", domain]
        output = self.runner(args)
        info = self._parse_dominfo(output)
        mem_value = info.get("Max memory", "0").split()[0]
        mem_gb = round(float(mem_value) / (1024 * 1024), 2)
        cpu_time_raw = info.get("CPU time", "0").split()[0]
        uptime_seconds = float(cpu_time_raw.rstrip("s"))
        return Workload(
            name=domain,
            workload_type="vm",
            vcpus=float(info.get("CPU(s)", "0")),
            memory_gb=mem_gb,
            utilization_cpu=0.0,
            utilization_memory=0.0,
            node=self.host_name,
            uptime_hours=uptime_seconds / 3600,
            labels={"state": info.get("State", "unknown")},
        )

    @staticmethod
    def _parse_dominfo(text: str) -> dict:
        info = {}
        for line in text.splitlines():
            if ":" in line:
                key, value = [part.strip() for part in line.split(":", 1)]
                info[key] = value
        return info
