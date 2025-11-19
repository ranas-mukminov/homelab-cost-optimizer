output "management_vmid" {
  value       = try(module.core_vms.vm_ids["mgmt"], null)
  description = "VMID of the management plane VM"
}

output "nas_id" {
  value       = proxmox_lxc.nas.id
  description = "Identifier of the NAS container"
}
