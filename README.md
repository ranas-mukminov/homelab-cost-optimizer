# 🏠 Homelab / SMB Infra-as-Code Blueprints & Cost Optimizer

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![CI](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Security Audit](https://github.com/ranas-mukminov/homelab-cost-optimizer/workflows/Security%20Audit/badge.svg)](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/security.yml)
[![Code Quality](https://github.com/ranas-mukminov/homelab-cost-optimizer/workflows/Code%20Quality/badge.svg)](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/code-quality.yml)

Opinionated IaC blueprints for homelabs and small businesses, plus an AI-assisted cost optimizer for your VMs and containers.

**Production-ready** | **Multi-platform** | **Cost-optimized** | **Infrastructure-as-Code**

---

## English

### 💡 Motivation

- 🏗️ Homelabs and SMB stacks grow organically without consistent documentation or reproducibility
- ⚡ Power usage and infra costs quietly increase while optimization remains a manual spreadsheet exercise
- 📚 Blog posts typically showcase a single bespoke lab, not a reusable, versioned blueprint catalog that can evolve with your hardware

### ✨ What this repository provides

#### 🛠️ IaC Blueprints:

- 🖥️ **Proxmox + OpenWrt + pfSense + NAS** baseline homelab
- ☸️ **K3s / K3d cluster** with CI/CD workers and an observability stack
- 🏢 **Home office stack** with VPN, SMB/NFS storage, backup, and monitoring glue
- 🚀 **Micro-SaaS** minimal production footprint with reverse proxy, TLS, app runtime, database, and scheduled backups

#### 💰 Cost Optimizer:

- 📊 Collects CPU/RAM/uptime and utilization metrics from Proxmox, libvirt, Docker, and Kubernetes APIs
- ⚡ Estimates power and monetary cost based on configurable power profiles and electricity tariffs
- 🔄 Suggests consolidation scenarios that merge low-utilization workloads or power down underused nodes
- 📝 Generates human-friendly Markdown or AI-crafted summaries with prioritized recommendations

### 🏗️ Architecture overview

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

- **Infrastructure layer**: Terraform modules define hypervisors, VLANs, and services; Ansible roles converge OS/services; k3d definitions bootstrap lightweight clusters for development mirrors
- **Optimizer layer**: pluggable collectors normalize usage, estimators quantify watts & currency, consolidator simulates right-sizing, reporters turn that story into actionable artifacts

### 🚀 Quick start

**Prerequisites:** Terraform, Ansible, k3d/k3s (if needed), Python 3.10+ with `pip`

**1. Clone repository:**
```bash
git clone https://github.com/ranas-mukminov/homelab-cost-optimizer && cd homelab-cost-optimizer
```

**2. Choose and configure blueprint:**
Pick a blueprint under `blueprints/terraform` and align variables (domain, VLANs, node inventory); pair with `blueprints/ansible` roles/playbooks.

**3. Deploy infrastructure:**
Run Terraform (with remote state) then Ansible to provision and configure the environment.

**4. Install optimizer:**
```bash
pip install -e .
homelab-cost-optimizer --help
```

**5. Configure electricity pricing:**
Copy `config/electricity.example.yaml` to `config/electricity.yaml` with your price per kWh.

**6. Run collection and analysis:**
```bash
homelab-cost-optimizer collect --source proxmox --url https://pve.local --token **** --out inventory.json
homelab-cost-optimizer analyze --input inventory.json --config config/electricity.yaml --out report.md
```

**7. Explore consolidation:**
```bash
homelab-cost-optimizer suggest --scenario consolidate-low-util --input data.json --config config/optimizer.yaml --ai-report
```

### 📁 Repository layout

- 📂 `blueprints/` – Terraform, Ansible, k3d, and AI helper modules composing the homelab catalogs
- 🐍 `optimizer/` – Python package with collectors, estimators, consolidators, reporters, and CLI
- 🤖 `ai_providers/` – Pluggable AI layer (OpenAI example + deterministic mock) for reports and blueprint assistants
- ⚙️ `config/` – Example YAML configs for electricity/cost and optimizer behavior
- 🧪 `tests/` – Unit + integration suites covering collectors through Terraform scaffolding sanity
- 🔧 `scripts/` – Linting, formatting, security, and performance automation helpers
- 🔄 `.github/workflows/` – CI pipelines for lint/tests and scheduled security scans
- 📄 `LEGAL.md`, `CONTRIBUTING.md`, `CHANGELOG.md` – governance and compliance docs

### 📦 Blueprints catalog (samples)

#### `proxmox-homelab`
- Spins up Proxmox hosts, pfSense/OPNsense firewall, dedicated NAS VM/LXC, and management jump host
- Focus on VLAN-aware networking, Ceph/ZFS storage pools, and DHCP/DNS integration

#### `k3s-ci-monitoring`
- Deploys lightweight K3s control plane + worker pool, Git server + CI runner, ArgoCD, Prometheus/Grafana, and Loki/Alertmanager wiring

#### `micro-saas`
- Templates for Traefik reverse proxy, TLS automation, app container set, PostgreSQL/Redis stateful components, backup CronJobs, and optional CDN/front-door integration
- Each blueprint exposes centralized `variables.tf` and Ansible group_vars so you can trace every subnet, credential, and resource sizing knob

### 💰 Cost optimizer

#### CLI usage (Typer-based):

```bash
# Collect metrics
homelab-cost-optimizer collect --source proxmox --url https://pve.local --token $PVE_TOKEN --out data.json

# Analyze costs
homelab-cost-optimizer analyze --input data.json --config config/electricity.yaml --out summary.md

# Get consolidation suggestions
homelab-cost-optimizer suggest --scenario consolidate-low-util --input data.json --config config/optimizer.yaml --ai-report
```

#### Features:

- **Data model**: Nodes carry type/power profiles; Workloads represent VMs, containers, or pods with assigned resources and utilization hints
- **Estimation**: Baseline idle watts per node + scaling for CPU cores and RAM; kWh derived from uptime hours × watts / 1000; currency via configurable tariff matrix
- **Consolidation**: Greedy bin-pack tries to fit workloads onto fewer nodes w/out exceeding CPU/RAM, reporting freed nodes, watts saved, and monthly deltas

### 🤖 AI integration

- 🎯 `blueprints/ai/blueprint_ai_adapter.py` consumes inventory and desired topology, optionally asks configured AI provider for alternative layouts, variable suggestions, or textual reasoning
- 📊 `optimizer/reporters/ai_reporter.py` converts numeric outcomes into narrative: headlines, prioritized recommendations, conservative vs aggressive scenarios, before/after comparison tables
- 🔌 AI providers live under `ai_providers/` with an abstract base and specific implementations; API keys are injected via environment variables, never stored in repo
- 🔒 Deterministic defaults ensure safe operation without AI credentials

### 🧪 Testing & quality

- ✅ `pytest` executes unit + integration suites
- 🔍 `scripts/lint.sh` runs Ruff/Black/isort, yamllint, terraform fmt/validate, ansible-lint
- 🔐 `scripts/security_scan.sh` runs `pip-audit` (or `safety`) and `bandit`
- ⚡ `scripts/perf_check.sh` spins synthetic datasets (100 nodes / 1000 workloads) to guard against pathological slowdowns

### ⚖️ Legal / responsible use

- ✅ Operate only on infrastructures and APIs you own or are authorized to assess
- 🔒 Respect Proxmox, libvirt, Docker, Kubernetes, and cloud provider terms of service; no credential scraping or bypass tooling is included
- 📊 Power/cost estimations are approximations for planning purposes, not financial advice or billing guarantees

### 👨‍💻 Professional services – run-as-daemon.ru

**Professional DevOps & Infrastructure services by [run-as-daemon.ru](https://run-as-daemon.ru)**

This project is maintained by the DevSecOps / SRE / FinOps engineer behind run-as-daemon.ru.

#### 💼 Services Offered:

- ��️ **Infrastructure as Code**: Designing reproducible homelab or SMB infrastructure as code
- ☸️ **Kubernetes & Orchestration**: Building K3s/Kubernetes clusters, CI/CD, and observability stacks
- 💰 **Cost Optimization**: Optimizing power and infrastructure costs of your existing workloads
- 📊 **Monitoring & Observability**: Setting up comprehensive monitoring solutions
- 🎓 **Training & Consulting**: Team workshops and infrastructure consulting

#### 📞 Contact for Consulting:

**Website:** [run-as-daemon.ru](https://run-as-daemon.ru)

*"Defense by design. Speed by default"* — Security-first architecture with performance optimization

---

### 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork and branch** per feature; keep changes focused
2. **Run quality checks:** `scripts/lint.sh`, `pytest`, and security/perf scripts before submitting PRs
3. **Blueprint contributions** should include diagrams/docs plus Terraform + Ansible parity; describe assumptions clearly
4. **Code style:** Follow the coding standards enforced by linters
5. **Documentation:** Update relevant docs with your changes

#### Development Guidelines:

- Keep changes focused and well-documented
- Add tests for new functionality
- Ensure all CI checks pass
- Follow conventional commits format

### 📄 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

---

## Русский (кратко)

### 🏠 О проекте

Каталог IaC-шаблонов для домашнего и SMB-оборудования с оптимизатором затрат на основе ИИ.

### ✨ Возможности:

#### 🛠️ IaC Blueprints:
- 🖥️ Proxmox + OpenWrt/pfSense + NAS
- ☸️ K3s/K3d кластеры с CI/CD и мониторингом
- 🏢 Домашний офис с VPN/файловыми сервисами/бэкапами
- 🚀 Минимальный micro-SaaS стек

#### 💰 Оптимизатор затрат:
- 📊 Собирает метрики из Proxmox, libvirt, Docker и Kubernetes
- ⚡ Оценивает энергопотребление по профилям мощности и тарифам
- 🔄 Предлагает сценарии консолидации
- 📝 Формирует отчёты (Markdown или AI)

### ⚠️ Важно:

- ✅ Используйте только на собственных системах
- 🔒 Уважайте ограничения API провайдеров
- 📊 Расчёты носят справочный характер

### 💼 Профессиональные услуги:

**[run-as-daemon.ru](https://run-as-daemon.ru)** — помощь с:
- 🏗️ Проектированием и внедрением Infrastructure as Code
- ☸️ Настройкой Kubernetes кластеров и CI/CD
- 💰 Оптимизацией затрат на инфраструктуру
- 📊 Внедрением систем мониторинга
- 🎓 Обучением команды DevOps практикам

---

## 📮 Support

**Community Support:**
- Open an issue on [GitHub Issues](https://github.com/ranas-mukminov/homelab-cost-optimizer/issues)
- Check existing issues for solutions
- Read documentation in the repository

**Professional Support:**
- Production infrastructure consulting
- Custom blueprint development
- Cost optimization analysis
- Training and workshops
- 24/7 support packages

**Contact:** [run-as-daemon.ru](https://run-as-daemon.ru)

---

**Made with ❤️ for homelab enthusiasts and SMB teams**

**Professional DevOps & Infrastructure Support:** [run-as-daemon.ru](https://run-as-daemon.ru)
