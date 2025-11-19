# Proxmox Homelab Blueprint

Opinionated Terraform configuration for a Proxmox-based homelab with pfSense/OpenWrt edge,
NAS services, and a management VM.

## Remote state
Configure a remote backend (S3, Terraform Cloud, GitLab, etc.) by adding the proper block in
`versions.tf`. For shared labs, keep one workspace per environment (lab, staging, prod) and
avoid local state files.

## Variables
| Name | Description |
| --- | --- |
| `proxmox_url` | Base URL of the Proxmox API (e.g., `https://pve.local:8006/api2/json`). |
| `proxmox_token_id` / `proxmox_token_secret` | API token credentials. |
| `resource_pool` | Proxmox pool hosting the blueprint assets. |
| `cloud_init_template` | Existing VM template for clones. |
| `core_vms` | Map keyed by VM name that describes CPU/RAM/disk/node placement. |
| `network_map` | VLAN IDs (WAN/LAN/mgmt). |
| `domain_name` | DNS suffix appended as VM tags. |
| `nas_storage_size_gb` | NAS rootfs size for the LXC appliance. |

## Usage
```bash
cd blueprints/terraform/proxmox-homelab
terraform init
terraform plan -var-file=homelab.tfvars
terraform apply
```

Pair this Terraform blueprint with the Ansible playbook `blueprints/ansible/playbooks/homelab.yaml`
to configure pfSense, OpenWrt, NAS exports, and monitoring agents.
