from __future__ import annotations

import logging
from typing import Dict, List, Optional

import requests

from ..models import Inventory, Node, PowerProfile, Workload
from .base import BaseCollector

LOGGER = logging.getLogger(__name__)


class ProxmoxCollector(BaseCollector):
    """Collect VM/node data from the Proxmox REST API."""

    def __init__(
        self,
        base_url: str,
        token_id: str,
        token_secret: str,
        power_profile: PowerProfile,
        verify_ssl: bool = True,
        timeout: int = 10,
    ) -> None:
        super().__init__(power_profile)
        self.base_url = base_url.rstrip("/")
        self.token_id = token_id
        self.token_secret = token_secret
        self.verify_ssl = verify_ssl
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}"}

    def _get(self, path: str) -> Dict:
        url = f"{self.base_url}{path}"
        response = requests.get(url, headers=self._headers(), verify=self.verify_ssl, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def collect(self) -> Inventory:
        nodes_data = self._get("/api2/json/nodes").get("data", [])
        vms_data = self._get("/api2/json/cluster/resources?type=vm").get("data", [])
        nodes = self._parse_nodes(nodes_data)
        workloads = self._parse_workloads(vms_data)
        return Inventory(nodes=nodes, workloads=workloads)

    def _parse_nodes(self, data: List[Dict]) -> List[Node]:
        nodes = []
        for item in data:
            total_memory_gb = self._bytes_to_gb(float(item.get("memory", item.get("maxmem", 0))))
            total_cpu = float(item.get("cpu", item.get("maxcpu", 0)))
            nodes.append(
                Node(
                    name=item.get("node", item.get("name", "unknown")),
                    kind="hypervisor",
                    total_cpu=total_cpu,
                    total_memory_gb=total_memory_gb,
                    power_profile=self.power_profile,
                    metadata={"status": item.get("status", "unknown"), "type": item.get("type", "node")},
                )
            )
        return nodes

    def _parse_workloads(self, data: List[Dict]) -> List[Workload]:
        workloads = []
        for item in data:
            total_memory_gb = self._bytes_to_gb(float(item.get("maxmem", 0)))
            workloads.append(
                Workload(
                    name=item.get("name", item.get("vmid", "vm")),
                    workload_type=item.get("type", "vm"),
                    vcpus=float(item.get("maxcpu", 0)),
                    memory_gb=total_memory_gb,
                    utilization_cpu=float(item.get("cpu", 0)),
                    utilization_memory=float(item.get("mem", 0)) / max(float(item.get("maxmem", 1)), 1),
                    node=item.get("node", ""),
                    uptime_hours=float(item.get("uptime", 0)) / 3600,
                    labels={"vmid": str(item.get("vmid"))},
                )
            )
        return workloads
