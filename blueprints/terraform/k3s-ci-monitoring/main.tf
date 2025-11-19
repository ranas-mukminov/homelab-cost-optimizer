provider "proxmox" {
  pm_api_url          = var.proxmox_url
  pm_api_token_id     = var.proxmox_token_id
  pm_api_token_secret = var.proxmox_token_secret
  pm_tls_insecure     = false
}

locals {
  controller_vm = [{
    name        = "${var.cluster_name}-ctrl"
    target_node = var.controller.target_node
    vmid        = var.controller.vmid
    cpu         = var.controller.cpu
    memory_mb   = var.controller.memory_mb
    disk_gb     = var.controller.disk_gb
    tags        = concat(var.controller.tags, ["controller"])
  }]

  worker_vms = [
    for worker in var.workers : {
      name        = "${var.cluster_name}-${worker.name}"
      target_node = worker.target_node
      vmid        = worker.vmid
      cpu         = worker.cpu
      memory_mb   = worker.memory_mb
      disk_gb     = worker.disk_gb
      tags        = concat(worker.tags, ["worker"])
    }
  ]

  git_stack = var.enable_git_stack ? [{
    name        = "${var.cluster_name}-git"
    target_node = var.controller.target_node
    vmid        = var.controller.vmid + 100
    cpu         = 4
    memory_mb   = 8192
    disk_gb     = 80
    tags        = ["git", "runner"]
  }] : []
}

module "cluster_vms" {
  source              = "../modules/proxmox_vm"
  instances           = concat(local.controller_vm, local.worker_vms, local.git_stack)
  pool                = var.resource_pool
  cloud_init_template = var.cloud_init_template
}
