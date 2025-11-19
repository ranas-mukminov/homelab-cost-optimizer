output "ingress_host" {
  description = "Public hostname"
  value       = var.domain
}

output "namespace" {
  value       = var.namespace
  description = "Namespace where resources were created"
}
