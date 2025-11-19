provider "kubernetes" {
  config_path = var.kubeconfig_path
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace
    labels = {
      "run-as-daemon.ru/stack" = "micro-saas"
    }
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = "app"
    namespace = var.namespace
    labels = {
      app = "saas"
    }
  }

  spec {
    replicas = var.app_replicas

    selector {
      match_labels = {
        app = "saas"
      }
    }

    template {
      metadata {
        labels = {
          app = "saas"
        }
      }

      spec {
        container {
          image = var.app_image
          name  = "web"

          port {
            container_port = 8080
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app" {
  metadata {
    name      = "app"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "saas"
    }

    port {
      port        = 80
      target_port = 8080
    }
  }
}

resource "kubernetes_ingress_v1" "app" {
  metadata {
    name      = "app"
    namespace = var.namespace
    annotations = {
      "kubernetes.io/ingress.class" = "traefik"
      "cert-manager.io/cluster-issuer" = "letsencrypt"
    }
  }

  spec {
    rule {
      host = var.domain

      http {
       path {
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                number = 80
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    tls {
      hosts      = [var.domain]
      secret_name = "${var.namespace}-tls"
    }
  }
}

resource "kubernetes_stateful_set_v1" "postgres" {
  count = var.enable_postgres ? 1 : 0

  metadata {
    name      = "postgres"
    namespace = var.namespace
  }

  spec {
    service_name = "postgres"
    replicas     = 1

    selector {
      match_labels = {
        app = "postgres"
      }
    }

    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }

      spec {
        container {
          image = "postgres:15"
          name  = "postgres"

          env {
            name  = "POSTGRES_DB"
            value = "app"
          }

          env {
            name  = "POSTGRES_USER"
            value = "app"
          }

          env {
            name  = "POSTGRES_PASSWORD"
            value = "changeme"
          }

          port {
            container_port = 5432
          }

          volume_mount {
            name       = "data"
            mount_path = "/var/lib/postgresql/data"
          }
        }
      }
    }

    volume_claim_template {
      metadata {
        name = "data"
      }

      spec {
        access_modes = ["ReadWriteOnce"]
        storage_class_name = var.postgres_storage_class

        resources {
          requests = {
            storage = "20Gi"
          }
        }
      }
    }
  }
}
