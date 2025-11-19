provider "proxmox" {
  pm_api_url          = var.proxmox_url
  pm_api_token_id     = var.proxmox_token_id
  pm_api_token_secret = var.proxmox_token_secret
  pm_tls_insecure     = var.proxmox_tls_insecure
}

locals {
  vm_list = [
    for name, cfg in var.core_vms : {
      name        = name
      target_node = cfg.target_node
      vmid        = cfg.vmid
      cpu         = cfg.cpu
      memory_mb   = cfg.memory_mb
      disk_gb     = cfg.disk_gb
      tags        = concat(cfg.tags, [var.domain_name])
      iso         = try(cfg.iso, null)
    }
  ]
}

module "core_vms" {
  source              = "../modules/proxmox_vm"
  instances           = local.vm_list
  pool                = var.resource_pool
  cloud_init_template = var.cloud_init_template
}

resource "proxmox_lxc" "nas" {
  hostname    = "nas"
  vmid        = 6000
  target_node = local.vm_list[0].target_node
  ostemplate  = "local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst"
  password    = "changeMe!"
  cores       = 4
  memory      = 8192

  rootfs {
    storage = "local-lvm"
    size    = "${var.nas_storage_size_gb}G"
  }

  network {
    name   = "eth0"
    bridge = "vmbr0"
    tag    = tonumber(var.network_map.management)
  }
}
