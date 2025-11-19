# Topology Overview

## Proxmox Homelab
```
[Internet] -> [pfSense VM] -> [OpenWrt edge] -> [Proxmox cluster]
                                    |-> [NAS VM + ZFS]
                                    |-> [Management VM]
```
- Dual NIC firewalls terminate WAN/LAN, VLAN aware.
- NAS exports NFS/iSCSI to hypervisors.
- Management VM hosts automation runners, monitoring, and VPN endpoints.

## K3s CI + Monitoring
```
[Proxmox] -> [K3s controller VM]
               |-> [Worker nodes]
               |-> [Git service + runner]
               |-> [ArgoCD + Prometheus + Grafana]
```
- Lightweight Git service (Gitea) and runner co-located with cluster.
- Observability stack monitors both workloads and host metrics.

## Micro-SaaS Stack
```
[Edge LB/Traefik] -> [App pods] -> [DB + backups]
                         |-> [Object storage sync]
```
- Traefik terminates TLS via ACME.
- Scheduled jobs export dumps to remote S3-compatible storage.
```
