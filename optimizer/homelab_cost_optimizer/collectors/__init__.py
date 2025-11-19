from __future__ import annotations

from typing import Dict, Type

from ..models import Inventory
from .base import BaseCollector
from .docker_collector import DockerCollector
from .k8s_collector import KubernetesCollector
from .libvirt_collector import LibvirtCollector
from .proxmox_collector import ProxmoxCollector

CollectorType = Type[BaseCollector]

COLLECTOR_REGISTRY: Dict[str, CollectorType] = {
    "proxmox": ProxmoxCollector,
    "libvirt": LibvirtCollector,
    "docker": DockerCollector,
    "k8s": KubernetesCollector,
}


def collect(source: str, **kwargs) -> Inventory:
    source = source.lower()
    if source not in COLLECTOR_REGISTRY:
        raise KeyError(f"Unsupported collector '{source}'. Available: {', '.join(COLLECTOR_REGISTRY)}")
    collector_cls = COLLECTOR_REGISTRY[source]
    collector: BaseCollector = collector_cls(**kwargs)
    return collector.collect()
