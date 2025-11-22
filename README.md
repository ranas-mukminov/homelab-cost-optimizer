# 🏠 Homelab Cost Optimizer

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![CI](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/homelab-cost-optimizer/actions/workflows/ci.yml)

🇬🇧 English | 🇷🇺 [Русская версия](README.ru.md)

---

## Overview

**Homelab Cost Optimizer** is a comprehensive infrastructure management toolkit for homelab enthusiasts and small business teams. It combines production-ready Infrastructure-as-Code (IaC) blueprints with an intelligent cost optimization engine that analyzes power consumption, resource utilization, and infrastructure expenses across multiple virtualization platforms.

This project helps Linux system administrators, DevOps engineers, and infrastructure teams reduce operational costs, standardize deployments, and maintain efficient homelab or SMB infrastructure without manual spreadsheet tracking.

## Key Features

- 🏗️ **Production-Ready IaC Blueprints** — Terraform and Ansible templates for common homelab stacks (Proxmox, K3s, NAS, VPN)
- 📊 **Multi-Platform Data Collection** — Gather metrics from Proxmox, libvirt, Docker, and Kubernetes APIs automatically
- ⚡ **Power Consumption Estimation** — Calculate electricity costs based on configurable power profiles and local tariffs
- 💰 **Cost Analysis Engine** — Track monthly infrastructure expenses and identify optimization opportunities
- 🔄 **Consolidation Recommendations** — AI-powered suggestions to merge low-utilization workloads and reduce active nodes
- 📝 **Automated Reporting** — Generate Markdown or AI-crafted summaries with actionable cost-saving recommendations
- 🤖 **AI Integration** — Optional OpenAI integration for intelligent blueprint suggestions and narrative reports
- 🔒 **Security-First Design** — No credential storage, API keys via environment variables, comprehensive security scanning

## Architecture / Components

The project consists of two main layers working together:

### Infrastructure Layer (blueprints/)

```
Terraform Modules ──┐
Ansible Playbooks ──┼──> Reproducible homelab stacks
K3d Definitions ────┘     (Proxmox, K3s, NAS, VPN, monitoring)
```

- **Terraform**: Infrastructure provisioning (VMs, networks, storage)
- **Ansible**: Configuration management (OS hardening, service deployment)
- **K3d**: Lightweight Kubernetes for development environments

### Optimizer Layer (optimizer/)

```
Data Collection ──> Normalization ──> Analysis ──> Recommendations
    |                    |                |              |
Proxmox API         Node/Workload    Power/Cost    Consolidation
libvirt API          Models         Estimators      Scenarios
Docker API                                              |
Kubernetes API                                   Markdown/AI Reports
```

**Data Flow:**
1. Collectors fetch resource metrics from infrastructure APIs
2. Unified models normalize data across different platforms
3. Estimators calculate power consumption and costs
4. Consolidators simulate optimization scenarios
5. Reporters generate actionable insights

## Requirements

### Operating System
- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+, Rocky Linux 8+)
- Any modern Linux distribution with Python 3.10+ support

### Infrastructure Access
- **For Blueprints**: Terraform 1.5+, Ansible 2.14+
- **For Optimizer**: API access to at least one platform:
  - Proxmox VE 7.0+ (API token required)
  - libvirt (socket access)
  - Docker Engine (socket access)
  - Kubernetes cluster (kubeconfig)

### System Resources
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for application, additional space for blueprints
- **Network**: Internet access for package installation and optional AI features

### Python Dependencies
- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Optional Components
- **OpenAI API key** — For AI-powered reports and blueprint assistance
- **k3d** — For local Kubernetes development (v5.4.0+)
- **Proxmox VE** — For homelab virtualization

## Quick Start (TL;DR)

```bash
# 1. Clone repository
git clone https://github.com/ranas-mukminov/homelab-cost-optimizer
cd homelab-cost-optimizer

# 2. Install optimizer
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 3. Configure electricity pricing
cp config/electricity.example.yaml config/electricity.yaml
# Edit config/electricity.yaml with your tariff

# 4. Collect metrics from your infrastructure
homelab-cost-optimizer collect \
  --source proxmox \
  --url https://pve.example.local:8006 \
  --token-id user@pam!tokenname \
  --token-secret YOUR_TOKEN_SECRET \
  --out inventory.json

# 5. Analyze costs
homelab-cost-optimizer analyze \
  --input inventory.json \
  --config config/electricity.yaml \
  --out report.md

# 6. Get consolidation suggestions
homelab-cost-optimizer suggest \
  --scenario consolidate-low-util \
  --input inventory.json \
  --config config/optimizer.yaml
```

**Default web access**: Cost reports are saved as Markdown files in the current directory.

## Detailed Installation

### Install on Ubuntu / Debian

```bash
# Update package index
sudo apt update

# Install Python 3.10+ and pip
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone https://github.com/ranas-mukminov/homelab-cost-optimizer
cd homelab-cost-optimizer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Install development tools (optional)
pip install -e .[dev]

# Verify installation
homelab-cost-optimizer --version
```

### Install on RHEL / Rocky / AlmaLinux

```bash
# Install Python 3.10+ and dependencies
sudo dnf install python3.10 python3.10-pip git -y

# Clone repository
git clone https://github.com/ranas-mukminov/homelab-cost-optimizer
cd homelab-cost-optimizer

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Verify installation
homelab-cost-optimizer --version
```

### Install with Docker / Docker Compose

```bash
# Clone repository
git clone https://github.com/ranas-mukminov/homelab-cost-optimizer
cd homelab-cost-optimizer

# Build container (example Dockerfile not included in repo)
# Note: Run directly with Python installation for best compatibility
```

**Note**: The project is designed to run directly on Linux systems. Container deployment is possible but not the primary use case.

### Install IaC Tools (for Blueprints)

```bash
# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Install Ansible
sudo apt install ansible -y

# Install k3d (for Kubernetes blueprints)
wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

## Configuration

### Electricity Pricing Configuration

Create `config/electricity.yaml` from the example:

```yaml
# Currency for cost calculations
currency: EUR

# Base electricity price per kilowatt-hour
price_per_kwh: 0.22

# Optional: Time-of-use pricing (peak/off-peak rates)
periods:
  - name: peak
    hours: ["08:00-22:00"]
    price_per_kwh: 0.26
  - name: offpeak
    hours: ["22:00-08:00"]
    price_per_kwh: 0.18
```

**Configuration options:**
- `currency` — Currency code for reports (EUR, USD, RUB, etc.)
- `price_per_kwh` — Default electricity price per kWh
- `periods` — Optional time-based pricing for peak/off-peak hours

### Optimizer Behavior Configuration

Create `config/optimizer.yaml` from the example:

```yaml
# Power consumption profiles for different hardware types
power_profiles:
  default:
    base_idle_watts: 65       # Idle power consumption
    watts_per_cpu_core: 12    # Additional watts per CPU core
    watts_per_gb_ram: 0.9     # Additional watts per GB of RAM
  
  low_power_node:
    base_idle_watts: 25
    watts_per_cpu_core: 7
    watts_per_gb_ram: 0.4

# Consolidation scenario parameters
scenarios:
  consolidate-low-util:
    cpu_threshold: 0.25       # Consolidate if CPU < 25%
    ram_threshold: 0.30       # Consolidate if RAM < 30%
    max_node_utilization: 0.70  # Don't exceed 70% after consolidation
  
  rightsize:
    cpu_headroom: 0.15        # Keep 15% CPU headroom
    ram_headroom: 0.20        # Keep 20% RAM headroom

# Reporting options
reporting:
  markdown_template: default
  enable_ai: false            # Set to true for AI-generated reports
```

### Environment Variables

```bash
# Optional: OpenAI API key for AI features
export OPENAI_API_KEY="sk-..."

# Optional: Proxmox credentials (alternative to command-line args)
export PROXMOX_URL="https://pve.example.local:8006"
export PROXMOX_TOKEN_ID="user@pam!tokenname"
export PROXMOX_TOKEN_SECRET="..."
```

## Usage & Common Tasks

### Collect Metrics from Infrastructure

**From Proxmox:**
```bash
homelab-cost-optimizer collect \
  --source proxmox \
  --url https://pve.example.local:8006 \
  --token-id user@pam!tokenname \
  --token-secret YOUR_SECRET \
  --out data/proxmox-inventory.json
```

**From Docker:**
```bash
homelab-cost-optimizer collect \
  --source docker \
  --socket /var/run/docker.sock \
  --out data/docker-inventory.json
```

**From Kubernetes:**
```bash
homelab-cost-optimizer collect \
  --source kubernetes \
  --kubeconfig ~/.kube/config \
  --out data/k8s-inventory.json
```

### Analyze Costs

```bash
# Generate cost analysis report
homelab-cost-optimizer analyze \
  --input data/inventory.json \
  --config config/electricity.yaml \
  --out reports/monthly-cost-analysis.md

# View report
cat reports/monthly-cost-analysis.md
```

### Get Consolidation Suggestions

```bash
# Basic consolidation suggestions
homelab-cost-optimizer suggest \
  --scenario consolidate-low-util \
  --input data/inventory.json \
  --config config/optimizer.yaml

# AI-powered recommendations (requires OpenAI API key)
export OPENAI_API_KEY="sk-..."
homelab-cost-optimizer suggest \
  --scenario consolidate-low-util \
  --input data/inventory.json \
  --config config/optimizer.yaml \
  --ai-report
```

### Deploy Infrastructure Blueprints

**Example: Proxmox Homelab Stack**

```bash
cd blueprints/terraform/proxmox-homelab

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var-file="vars/production.tfvars"

# Apply infrastructure
terraform apply -var-file="vars/production.tfvars"

# Configure with Ansible
cd ../../ansible
ansible-playbook -i inventory/homelab playbooks/configure-proxmox.yml
```

## Update / Upgrade

### Update Optimizer Tool

```bash
# Navigate to repository
cd homelab-cost-optimizer

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Reinstall package
pip install -e . --upgrade

# Verify version
homelab-cost-optimizer --version
```

### Update Infrastructure Blueprints

```bash
# Pull latest blueprint updates
git pull origin main

# Review changes in blueprints/
git log --oneline blueprints/

# Re-run Terraform plan to see infrastructure changes
cd blueprints/terraform/<blueprint-name>
terraform plan

# Apply updates carefully
terraform apply
```

## Logs, Monitoring, Troubleshooting

### Application Logs

The optimizer outputs logs to stdout/stderr by default:

```bash
# Enable verbose logging
homelab-cost-optimizer collect --source proxmox ... --verbose

# Redirect logs to file
homelab-cost-optimizer analyze ... 2>&1 | tee optimizer.log
```

### Common Issues and Solutions

**Problem: `ModuleNotFoundError: No module named 'homelab_cost_optimizer'`**

```bash
# Solution: Install package in virtual environment
source venv/bin/activate
pip install -e .
```

**Problem: Proxmox API connection refused or timeout**

```bash
# Check network connectivity
ping pve.example.local

# Verify Proxmox API is accessible
curl -k https://pve.example.local:8006/api2/json/version

# Check firewall rules allow port 8006
sudo ufw status
```

**Problem: Permission denied accessing Docker socket**

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo (not recommended)
sudo homelab-cost-optimizer collect --source docker ...
```

**Problem: No data in cost reports**

```bash
# Verify inventory file contains data
cat data/inventory.json | jq .

# Check electricity config is loaded
homelab-cost-optimizer analyze ... --verbose
```

**Problem: AI features not working**

```bash
# Verify OpenAI API key is set
echo $OPENAI_API_KEY

# Install AI dependencies
pip install -e .[ai]

# Check OpenAI API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Security Notes

### Access Control

- 🔒 **Change default credentials** — Never use default passwords for Proxmox, Docker, or Kubernetes access
- 🔐 **Use API tokens** — Prefer token-based authentication over username/password
- 🚫 **Restrict API access** — Configure firewall rules to limit API endpoint access to trusted networks
- 🔑 **Rotate credentials** — Regularly rotate API tokens and access keys

### Network Security

- 🛡️ **Use VPN or SSH tunnels** — Access infrastructure APIs through encrypted connections
- 🌐 **Don't expose APIs publicly** — Keep Proxmox, libvirt, and Docker APIs on internal networks
- 🔥 **Configure firewalls** — Use UFW, iptables, or network firewalls to restrict access

### Data Privacy

- 📊 **Inventory data** — Generated JSON files may contain infrastructure details; store securely
- 🗑️ **Clean up reports** — Remove old reports containing sensitive infrastructure information
- 🔒 **API keys** — Never commit API keys or tokens to version control

### Compliance

- ✅ **Operate only on authorized infrastructure** — Collect metrics only from systems you own or manage
- 📜 **Respect API terms of service** — Follow Proxmox, Docker, and Kubernetes usage policies
- ⚖️ **Financial estimates are informational** — Cost calculations are approximations, not billing guarantees

## Project Structure

```
homelab-cost-optimizer/
├── blueprints/              # IaC templates and automation
│   ├── terraform/           # Infrastructure provisioning modules
│   ├── ansible/             # Configuration management playbooks
│   ├── k3d/                 # Kubernetes development environments
│   └── ai/                  # AI-powered blueprint helpers
├── optimizer/               # Python package (cost optimizer)
│   └── homelab_cost_optimizer/
│       ├── cli.py           # Command-line interface
│       ├── collectors/      # Data collection from APIs
│       ├── estimators/      # Power and cost calculations
│       ├── consolidators/   # Optimization algorithms
│       └── reporters/       # Report generation
├── ai_providers/            # AI integration layer
│   ├── base.py              # Abstract AI provider interface
│   ├── openai_provider.py  # OpenAI implementation
│   └── mock_provider.py    # Deterministic mock for testing
├── config/                  # Example configurations
│   ├── electricity.example.yaml
│   └── optimizer.example.yaml
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── scripts/                 # Development and CI helpers
│   ├── lint.sh              # Code quality checks
│   ├── security_scan.sh     # Security audits
│   └── perf_check.sh        # Performance benchmarks
├── .github/workflows/       # CI/CD pipelines
├── LEGAL.md                 # Legal and compliance notes
├── CONTRIBUTING.md          # Contribution guidelines
├── CHANGELOG.md             # Version history
└── LICENSE                  # Apache-2.0 license
```

## Roadmap / Plans

**Planned features** (contributions welcome):

- 🌍 **Additional platform support** — VMware ESXi, OpenStack, LXC/LXD collectors
- 📊 **Grafana dashboard integration** — Real-time cost monitoring
- 🔄 **Automated consolidation** — Execute optimization recommendations automatically
- 💾 **Historical tracking** — Database backend for cost trend analysis
- 🌡️ **Temperature monitoring** — Correlate power consumption with thermal data
- ☁️ **Cloud cost comparison** — Compare on-premise vs cloud provider pricing

**Long-term vision:**

- Complete observability stack blueprints
- Multi-site homelab orchestration
- Energy efficiency scoring and benchmarks

## Contributing

Contributions are welcome and appreciated! Follow these guidelines:

### How to Contribute

**1. Open an issue** — Discuss bugs, feature requests, or blueprint ideas in [GitHub Issues](https://github.com/ranas-mukminov/homelab-cost-optimizer/issues)

**2. Fork and branch** — Create a feature branch from `main`:
```bash
git checkout -b feature/your-feature-name
```

**3. Follow code style:**
- Python: PEP 8 compliance, type hints, 100-character line length
- Use Black formatter: `black .`
- Use isort for imports: `isort .`
- Terraform: `terraform fmt`
- Ansible: `ansible-lint`

**4. Add tests** — New features require unit tests and integration tests where applicable:
```bash
pytest tests/
```

**5. Run quality checks:**
```bash
# Lint and format
scripts/lint.sh

# Security scan
scripts/security_scan.sh

# Performance check
scripts/perf_check.sh
```

**6. Submit pull request** — Provide clear description of changes and motivation

### Blueprint Contributions

When contributing new IaC blueprints:

- Include both Terraform and Ansible components
- Document all variables and assumptions
- Provide example `tfvars` and inventory files
- Add README in blueprint directory
- Test against fresh installations

### Code Review Process

- All PRs require passing CI checks
- Maintainers review within 3-5 business days
- Address review feedback before merge

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

**Summary:**
- ✅ Free to use, modify, and distribute
- ✅ Can be used commercially
- ✅ Patent grant included
- ⚠️ Must include license and copyright notices
- ⚠️ Changes must be documented

## Author and Commercial Support

**Author:** [Ranas Mukminov](https://github.com/ranas-mukminov)

**Professional DevOps & Infrastructure Services:** [run-as-daemon.ru](https://run-as-daemon.ru)

### Commercial Support Services

For production deployments, custom solutions, and professional assistance:

- 🏗️ **Infrastructure Design & Implementation** — Custom homelab and SMB infrastructure architecture
- ☸️ **Kubernetes & Orchestration** — K3s/K8s cluster setup, CI/CD pipelines, observability stacks
- 💰 **Cost Optimization Consulting** — Deep analysis and optimization of your infrastructure expenses
- 📊 **Monitoring & Observability** — Prometheus, Grafana, Loki implementation and tuning
- 🎓 **Training & Workshops** — Team training on IaC, DevOps practices, and cost management
- 🔒 **Security Audits** — Infrastructure security reviews and hardening

**Contact:** [run-as-daemon.ru](https://run-as-daemon.ru) or via [GitHub profile](https://github.com/ranas-mukminov)

---

**Made with ❤️ for homelab enthusiasts and SMB teams**

**Professional Support:** [run-as-daemon.ru](https://run-as-daemon.ru)
