# homelab-cost-optimizer Package

This directory houses the Python package consumed by the CLI entry point. It includes collectors
for multiple platforms, estimators for power/cost, consolidation heuristics, and a set of
reporters (text, Markdown, AI).

```bash
pip install -e .
homelab-cost-optimizer --help
```

Key modules:
- `collectors/`: Normalize usage from Proxmox, libvirt, Docker, Kubernetes.
- `estimators/`: Compute wattage and monetary impact from workloads.
- `consolidators/`: Greedy bin-packing simulations for consolidation and right-sizing.
- `reporters/`: Produce text/Markdown/AI narratives.
- `config.py`: YAML helpers for electricity + optimizer settings.
- `cli.py`: Typer-based command group.
