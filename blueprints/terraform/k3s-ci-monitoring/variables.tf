variable "proxmox_url" {
  type        = string
  description = "Proxmox API URL"
}

variable "proxmox_token_id" {
  type        = string
  description = "Proxmox token ID"
}

variable "proxmox_token_secret" {
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  type        = string
  description = "Prefix for VMs and resources"
}

variable "resource_pool" {
  type        = string
  description = "Proxmox pool"
}

variable "cloud_init_template" {
  type        = string
  description = "Template used for clones"
}

variable "controller" {
  description = "Controller VM definition"
  type = object({
    target_node = string
    vmid        = number
    cpu         = number
    memory_mb   = number
    disk_gb     = number
    tags        = list(string)
  })
}

variable "workers" {
  description = "Worker VM definitions"
  type = list(object({
    name        = string
    target_node = string
    vmid        = number
    cpu         = number
    memory_mb   = number
    disk_gb     = number
    tags        = list(string)
  }))
}

variable "enable_git_stack" {
  description = "Provision Git service/runner nodes"
  type        = bool
  default     = true
}
