output "ansible_inventory" {
  description = "Inventory entries for controller/workers"
  value = {
    controller = local.controller_vm
    workers    = local.worker_vms
    git_stack  = local.git_stack
  }
}
