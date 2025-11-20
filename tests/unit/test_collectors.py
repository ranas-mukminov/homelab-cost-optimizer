from __future__ import annotations

import json

from homelab_cost_optimizer.collectors.docker_collector import DockerCollector
from homelab_cost_optimizer.collectors.k8s_collector import KubernetesCollector
from homelab_cost_optimizer.collectors.libvirt_collector import LibvirtCollector
from homelab_cost_optimizer.collectors.proxmox_collector import ProxmoxCollector
from homelab_cost_optimizer.models import PowerProfile

PROFILE = PowerProfile(
    name="default", base_idle_watts=60, watts_per_cpu_core=10, watts_per_gb_ram=1
)


def test_proxmox_collector_parses(monkeypatch):
    collector = ProxmoxCollector(
        base_url="https://pve.local:8006",
        token_id="user@pam!token",
        token_secret="secret",
        power_profile=PROFILE,
    )

    def fake_get(path: str):
        if path.endswith("nodes"):
            return {"data": [{"node": "pve1", "maxcpu": 16, "maxmem": 17179869184}]}
        return {
            "data": [
                {
                    "name": "vm1",
                    "vmid": 100,
                    "type": "qemu",
                    "maxcpu": 2,
                    "maxmem": 2147483648,
                    "node": "pve1",
                    "cpu": 0.25,
                    "mem": 1073741824,
                    "uptime": 3600,
                }
            ]
        }

    monkeypatch.setattr(collector, "_get", fake_get)
    inventory = collector.collect()
    assert inventory.nodes[0].name == "pve1"
    assert inventory.workloads[0].name == "vm1"
    assert inventory.workloads[0].uptime_hours == 1


def test_libvirt_collector(monkeypatch):
    list_output = """ Id    Name                           State\n----------------------------------------------------\n 1     vm1                            running\n -     vm2                            shut off\n"""
    dominfo_running = """Id: 1\nName: vm1\nCPU(s): 2\nMax memory: 4194304 KiB\nState: running\nCPU time: 7200.0s\n"""
    dominfo_shutdown = """Id: -\nName: vm2\nCPU(s): 2\nMax memory: 2097152 KiB\nState: shut off\nCPU time: 0.0s\n"""

    def fake_runner(args):
        if "list" in args:
            return list_output
        if args[-1] == "vm1":
            return dominfo_running
        return dominfo_shutdown

    collector = LibvirtCollector(power_profile=PROFILE, runner=fake_runner)
    inventory = collector.collect()
    assert len(inventory.workloads) == 2
    assert inventory.workloads[0].node == collector.host_name


def test_docker_collector_parses(tmp_path):
    fake_stats = "container1,5.0%,128MiB / 8GiB\ncontainer2,1.0%,512MiB / 8GiB"
    collector = DockerCollector(power_profile=PROFILE, runner=lambda args: fake_stats)
    inventory = collector.collect()
    assert len(inventory.workloads) == 2
    assert inventory.workloads[0].workload_type == "container"


def test_k8s_collector_parses(monkeypatch):
    nodes_json = {
        "items": [
            {
                "metadata": {"name": "node1", "labels": {"role": "worker"}},
                "status": {"capacity": {"cpu": "2", "memory": "4096Mi"}},
            }
        ]
    }
    pods_json = {
        "items": [
            {
                "metadata": {"name": "pod1", "labels": {}},
                "spec": {
                    "nodeName": "node1",
                    "containers": [{"resources": {"requests": {"cpu": "250m", "memory": "256Mi"}}}],
                },
            }
        ]
    }

    def fake_runner(args):
        if args[-2:] == ["-o", "json"] and "nodes" in args:
            return json.dumps(nodes_json)
        return json.dumps(pods_json)

    collector = KubernetesCollector(power_profile=PROFILE, runner=fake_runner)
    inventory = collector.collect()
    assert inventory.nodes[0].total_cpu == 2
    assert inventory.workloads[0].node == "node1"
