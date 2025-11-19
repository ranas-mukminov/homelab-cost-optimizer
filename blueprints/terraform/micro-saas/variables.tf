variable "kubeconfig_path" {
  description = "Path to kubeconfig used by kubernetes provider"
  type        = string
}

variable "namespace" {
  description = "Namespace for the micro-SaaS stack"
  type        = string
  default     = "micro-saas"
}

variable "app_image" {
  description = "Container image for the application"
  type        = string
}

variable "app_replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 2
}

variable "domain" {
  description = "Public domain served by Traefik"
  type        = string
}

variable "enable_postgres" {
  description = "Deploy managed PostgreSQL via StatefulSet"
  type        = bool
  default     = true
}

variable "postgres_storage_class" {
  description = "StorageClass for PostgreSQL PVC"
  type        = string
  default     = "local-path"
}
