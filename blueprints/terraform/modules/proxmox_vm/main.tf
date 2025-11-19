resource "proxmox_vm_qemu" "this" {
  for_each = { for vm in var.instances : vm.name => vm }

  name        = each.value.name
  target_node = each.value.target_node
  vmid        = each.value.vmid
  pool        = var.pool
  clone       = var.cloud_init_template
  cores       = each.value.cpu
  sockets     = 1
  memory      = each.value.memory_mb
  onboot      = true
  tags        = join(",", each.value.tags)

  disk {
    slot     = 0
    size     = "${each.value.disk_gb}G"
    type     = "scsi"
    storage  = "local-lvm"
    iothread = 1
  }

  network {
    model  = "virtio"
    bridge = "vmbr0"
  }

  lifecycle {
    create_before_destroy = true
  }
}

output "vm_ids" {
  value = { for name, vm in proxmox_vm_qemu.this : name => vm.id }
}
