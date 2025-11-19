variable "instances" {
  description = "List of Proxmox VM definitions"
  type = list(object({
    name        = string
    target_node = string
    vmid        = number
    cpu         = number
    memory_mb   = number
    disk_gb     = number
    tags        = list(string)
    iso         = optional(string, null)
  }))
}

variable "pool" {
  description = "Proxmox resource pool"
  type        = string
}

variable "cloud_init_template" {
  description = "Existing cloud-init template ID"
  type        = string
}
