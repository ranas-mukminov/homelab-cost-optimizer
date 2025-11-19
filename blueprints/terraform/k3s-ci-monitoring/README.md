# K3s + CI/Monitoring Blueprint

Creates controller and worker VMs for a lightweight K3s cluster along with optional Git service
and runner nodes.

## Highlights
- Templated Proxmox clones for controller/worker nodes.
- Optional Git service (Gitea) and CI runner host.
- Outputs machine inventory for downstream Ansible playbooks that bootstrap K3s, Git service,
and observability stack (Prometheus/Grafana).

## Usage
```bash
cd blueprints/terraform/k3s-ci-monitoring
terraform init
terraform plan -var-file=cluster.tfvars
terraform apply
```

After Terraform, run `blueprints/ansible/playbooks/smb-office.yaml` or `homelab.yaml` to configure
packages, install K3s, and deploy Helm releases.
