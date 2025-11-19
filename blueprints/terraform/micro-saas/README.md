# Micro-SaaS Stack Blueprint

Deploys a minimal production stack in Kubernetes/k3s consisting of an application Deployment,
ClusterIP Service, Traefik Ingress, and optional PostgreSQL StatefulSet.

## Prereqs
- Existing Kubernetes or k3s cluster (pair with `k3d/clusters` for dev/testing).
- Traefik ingress controller with cert-manager (or adapt the annotations).
- StorageClass for PostgreSQL PVC (default `local-path`).

## Usage
```bash
cd blueprints/terraform/micro-saas
terraform init
terraform plan -var kubeconfig_path=$KUBECONFIG -var app_image=ghcr.io/acme/app:main -var domain=app.example.com
terraform apply
```

Outputs report the namespace and ingress host to integrate with DNS/monitoring. Complete the
stack by applying `blueprints/ansible/playbooks/micro-saas.yaml` for OS-level backup tasks and
`blueprints/ai` helper for sizing suggestions.
