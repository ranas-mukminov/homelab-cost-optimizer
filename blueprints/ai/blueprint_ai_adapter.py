from __future__ import annotations

from typing import Dict, List, Optional

from ai_providers import ProviderNotAvailable, get_provider


def suggest_blueprint_variables(
    topology: str,
    hardware_inventory: List[Dict[str, str | int | float]],
    provider: str | None = None,
) -> Dict[str, str]:
    """Return suggested variable values for a topology.

    Deterministic defaults are always provided. If an AI provider is configured it is used
    to enrich the explanation and provide extra knobs.
    """

    defaults = _deterministic_defaults(topology, hardware_inventory)
    if not provider:
        return defaults

    try:
        ai = get_provider(provider)
    except ProviderNotAvailable:
        return defaults

    context = {"topology": topology, "nodes": hardware_inventory, "defaults": defaults}
    explanation = ai.generate_blueprint_suggestions(context)
    defaults["ai_summary"] = explanation
    return defaults


def _deterministic_defaults(topology: str, hardware_inventory: List[Dict[str, str | int | float]]) -> Dict[str, str]:
    capacity = sum(int(node.get("memory_gb", 16)) for node in hardware_inventory)
    nodes = len(hardware_inventory) or 1
    if topology == "proxmox-homelab":
        return {
            "proxmox_node_count": str(nodes),
            "recommended_ceph_size": "small" if capacity < 128 else "medium",
            "wan_firewall": "pfSense",
            "ai_summary": "Deterministic mapping applied (no AI)",
        }
    if topology == "k3s-ci-monitoring":
        return {
            "controller_count": "1",
            "worker_count": str(max(nodes - 1, 1)),
            "enable_git_runner": "true",
            "ai_summary": "Deterministic mapping applied (no AI)",
        }
    return {
        "edge_proxy": "traefik",
        "app_replicas": str(max(nodes, 2)),
        "backup_window": "02:00",
        "ai_summary": "Deterministic mapping applied (no AI)",
    }
