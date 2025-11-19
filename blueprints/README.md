# homelab-blueprints-run-as-daemon

This catalog contains Terraform, Ansible, and k3d assets intended to bootstrap homelab and
SMB-friendly topologies. Mix and match blueprints depending on the hypervisor/stack you run.

## Contents
- `docs/topology-overview.md` – high-level diagrams and narrative.
- `terraform/` – declarative infrastructure blueprints (Proxmox homelab, K3s CI/monitoring, micro-SaaS stack).
- `ansible/` – roles and playbooks covering firmware/OS/services post-provisioning.
- `k3d/` – lightweight cluster definitions for local dev/test mirrors.
- `ai/blueprint_ai_adapter.py` – optional AI helper to suggest variable values and explain decisions.

Each Terraform blueprint ships with its own README, remote state recommendations, and
parameter tables. Ansible roles default to idempotent tasks and expose variables via
`defaults/main.yml`.
