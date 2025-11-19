variable "proxmox_url" {
  description = "Base URL to the Proxmox API"
  type        = string
}

variable "proxmox_token_id" {
  description = "API token id in the format user@pam!token"
  type        = string
}

variable "proxmox_token_secret" {
  description = "API token secret"
  type        = string
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  description = "Allow TLS verification to be skipped"
  type        = bool
  default     = false
}

variable "resource_pool" {
  description = "Proxmox pool name for blueprint resources"
  type        = string
}

variable "cloud_init_template" {
  description = "Template VM ID used for clones"
  type        = string
}

variable "core_vms" {
  description = "Map describing firewall, edge router, NAS, and management VMs"
  type = map(object({
    target_node = string
    vmid        = number
    cpu         = number
    memory_mb   = number
    disk_gb     = number
    tags        = list(string)
    iso         = optional(string)
  }))
}

variable "network_map" {
  description = "VLAN/tag definitions for wan/lan/management"
  type = object({
    wan        = string
    lan        = string
    management = string
  })
}

variable "domain_name" {
  description = "Primary DNS domain"
  type        = string
}

variable "nas_storage_size_gb" {
  description = "Total NAS storage to allocate"
  type        = number
  default     = 2048
}
