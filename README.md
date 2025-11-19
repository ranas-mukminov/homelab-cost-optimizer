# Homelab / SMB Infra-as-Code Blueprints & Cost Optimizer

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![CI](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)

> Opinionated IaC blueprints for homelabs and small businesses, plus an AI-assisted cost optimizer for your VMs and containers.

## English

### Motivation
- Homelabs and SMB stacks grow organically without consistent documentation or reproducibility.
- Power usage and infra costs quietly increase while optimization remains a manual spreadsheet exercise.
- Blog posts typically showcase a single bespoke lab, not a reusable, versioned blueprint catalog that can evolve with your hardware.

### What this repository provides
- **IaC blueprints** covering:
  - Proxmox + OpenWrt + pfSense + NAS baseline homelab.
  - K3s / K3d cluster with CI/CD workers and an observability stack.
  - Home office stack with VPN, SMB/NFS storage, backup, and monitoring glue.
  - Micro-SaaS minimal production footprint with reverse proxy, TLS, app runtime, database, and scheduled backups.
- **Cost optimizer** that:
  - Collects CPU/RAM/uptime and utilization metrics from Proxmox, libvirt, Docker, and Kubernetes APIs.
  - Estimates power and monetary cost based on configurable power profiles and electricity tariffs.
  - Suggests consolidation scenarios that merge low-utilization workloads or power down underused nodes.
  - Generates human-friendly Markdown or AI-crafted summaries with prioritized recommendations.

### Architecture overview
```
Terraform/Ansible/k3d blueprints --> reproducible lab + SMB stacks
                                      |  
                                      | collectors (Proxmox/libvirt/Docker/K8s)
                                      v
                                 unified models (Nodes, Workloads)
                                      |
             power estimator ---- cost estimator ---- heuristic consolidator
                                      |
                     text/markdown/AI reporters --> operators + stakeholders
```
- Infrastructure layer: Terraform modules define hypervisors, VLANs, and services; Ansible roles converge OS/services; k3d definitions bootstrap lightweight clusters for development mirrors.
- Optimizer layer: pluggable collectors normalize usage, estimators quantify watts & currency, consolidator simulates right-sizing, reporters turn that story into actionable artifacts.

### Quick start
1. Install requirements: Terraform, Ansible, k3d/k3s (if needed), Python 3.10+ with `pip`.
2. Clone repo: `git clone https://github.com/ranas-mukminov/homelab-cost-optimizer && cd homelab-cost-optimizer`.
3. Pick a blueprint under `blueprints/terraform` and align variables (domain, VLANs, node inventory); pair with `blueprints/ansible` roles/playbooks.
4. Run Terraform (with remote state) then Ansible to provision and configure the environment.
5. Install optimizer locally:
   ```bash
   pip install -e .
   homelab-cost-optimizer --help
   ```
6. Copy `config/electricity.example.yaml` to `config/electricity.yaml` with your price per kWh.
7. Run a collection + analysis cycle:
   ```bash
   homelab-cost-optimizer collect --source proxmox --url https://pve.local --token **** --out inventory.json
   homelab-cost-optimizer analyze --input inventory.json --config config/electricity.yaml --out report.md
   ```
8. Iterate with consolidation scenarios via `homelab-cost-optimizer suggest`.

### Repository layout
- `blueprints/` – Terraform, Ansible, k3d, and AI helper modules composing the homelab catalogs.
- `optimizer/` – Python package with collectors, estimators, consolidators, reporters, and CLI.
- `ai_providers/` – Pluggable AI layer (OpenAI example + deterministic mock) for reports and blueprint assistants.
- `config/` – Example YAML configs for electricity/cost and optimizer behavior.
- `tests/` – Unit + integration suites covering collectors through Terraform scaffolding sanity.
- `scripts/` – Linting, formatting, security, and performance automation helpers.
- `.github/workflows/` – CI pipelines for lint/tests and scheduled security scans.
- `LEGAL.md`, `CONTRIBUTING.md`, `CHANGELOG.md` – governance and compliance docs.

### Blueprints catalog (samples)
- `proxmox-homelab`:
  - Spins up Proxmox hosts, pfSense/OPNsense firewall, dedicated NAS VM/LXC, and management jump host.
  - Focus on VLAN-aware networking, Ceph/ZFS storage pools, and DHCP/DNS integration.
- `k3s-ci-monitoring`:
  - Deploys lightweight K3s control plane + worker pool, Git server + CI runner, ArgoCD, Prometheus/Grafana, and Loki/Alertmanager wiring.
- `micro-saas`:
  - Templates for Traefik reverse proxy, TLS automation, app container set, PostgreSQL/Redis stateful components, backup CronJobs, and optional CDN/front-door integration.
- Each blueprint exposes centralized `variables.tf` and Ansible group_vars so you can trace every subnet, credential, and resource sizing knob.

### Cost optimizer
- **CLI usage** (Typer-based):
  - `homelab-cost-optimizer collect --source proxmox --url https://pve.local --token $PVE_TOKEN --out data.json`
  - `homelab-cost-optimizer analyze --input data.json --config config/electricity.yaml --out summary.md`
  - `homelab-cost-optimizer suggest --scenario consolidate-low-util --input data.json --config config/optimizer.yaml --ai-report`
- **Data model**: Nodes carry type/power profiles; Workloads represent VMs, containers, or pods with assigned resources and utilization hints.
- **Estimation**: Baseline idle watts per node + scaling for CPU cores and RAM; kWh derived from uptime hours * watts / 1000; currency via configurable tariff matrix.
- **Consolidation**: Greedy bin-pack tries to fit workloads onto fewer nodes w/out exceeding CPU/RAM, reporting freed nodes, watts saved, and monthly deltas.

### AI integration
- `blueprints/ai/blueprint_ai_adapter.py` consumes inventory and desired topology, optionally asks configured AI provider for alternative layouts, variable suggestions, or textual reasoning. Deterministic defaults ensure safe operation without AI credentials.
- `optimizer/reporters/ai_reporter.py` converts numeric outcomes into narrative: headlines, prioritized recommendations, conservative vs aggressive scenarios, before/after comparison tables.
- AI providers live under `ai_providers/` with an abstract base and specific implementations; API keys are injected via environment variables, never stored in repo.

### Testing & quality
- `pytest` executes unit + integration suites.
- `scripts/lint.sh` runs Ruff/Black/isort, yamllint, terraform fmt/validate, ansible-lint.
- `scripts/security_scan.sh` runs `pip-audit` (or `safety`) and `bandit`.
- `scripts/perf_check.sh` spins synthetic datasets (100 nodes / 1000 workloads) to guard against pathological slowdowns.

### Legal / responsible use
- Operate only on infrastructures and APIs you own or are authorized to assess.
- Respect Proxmox, libvirt, Docker, Kubernetes, and cloud provider terms of service; no credential scraping or bypass tooling is included.
- Power/cost estimations are approximations for planning purposes, not financial advice or billing guarantees.

### Professional services — run-as-daemon.ru
**Professional services by [run-as-daemon.ru](https://run-as-daemon.ru)**
If you need expert guidance for:
- Designing reproducible homelab or SMB infrastructure as code.
- Building K3s/Kubernetes clusters, CI/CD, and observability stacks.
- Optimizing power and infrastructure costs of your existing workloads.
Reach out for consulting, implementation, and ongoing support from the DevSecOps / SRE / FinOps engineer behind run-as-daemon.ru.

### Contributing
- Fork and branch per feature; keep changes focused.
- Run `scripts/lint.sh`, `pytest`, and security/perf scripts before submitting PRs.
- Blueprint contributions should include diagrams/docs plus Terraform + Ansible parity; describe assumptions clearly.

### License
- Apache-2.0, see [LICENSE](LICENSE).

---

## Русский (кратко)
- Каталог IaC-шаблонов для домашнего и SMB-оборудования: Proxmox + OpenWrt/pfSense + NAS, K3s/K3d кластеры с CI/CD и мониторингом, домашний офис с VPN/файловыми сервисами/бэкапами, минимальный micro-SaaS стек.
- Оптимизатор затрат собирает метрики из Proxmox, libvirt, Docker и Kubernetes, оценивает энергопотребление по профилям мощности и тарифам, предлагает сценарии консолидации и формирует отчёты (Markdown или AI).
- Используйте только на собственных системах, уважайте ограничения API; расчёты носят справочный характер.
- Профессиональные услуги и поддержка доступны на [run-as-daemon.ru](https://run-as-daemon.ru).
