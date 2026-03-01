terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    # Configure with: terraform init -backend-config="bucket=YOUR_BUCKET_NAME"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  # Fail fast if Tailscale is enabled without an auth key
  _tailscale_key_check = (
    var.tailscale_enabled && var.tailscale_auth_key == ""
    ? tobool("tailscale_auth_key is required when tailscale_enabled is true")
    : true
  )
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudrun.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "vpcaccess.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

# VPC Network for private services
resource "google_compute_network" "vpc" {
  name                    = "pr-helper-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

resource "google_compute_subnetwork" "subnet" {
  name          = "pr-helper-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Allocate IP range for private service connection
resource "google_compute_global_address" "private_ip_range" {
  name          = "pr-helper-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Create private VPC connection for Cloud SQL
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
  depends_on              = [google_project_service.apis]
}

# Serverless VPC Access Connector
resource "google_vpc_access_connector" "connector" {
  name          = "pr-helper-connector"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  depends_on    = [google_project_service.apis]
}

# Service Account for Cloud Run services
resource "google_service_account" "cloud_run" {
  account_id   = "pr-helper-cloudrun"
  display_name = "PR Helper Cloud Run Service Account"
}

# IAM roles for Cloud Run service account
resource "google_project_iam_member" "cloud_run_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud SQL PostgreSQL instance with private IP
resource "google_sql_database_instance" "postgres" {
  name             = "pr-helper-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = false
      start_time                     = "03:00"
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = var.environment == "production"
  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_project_service.apis
  ]
}

resource "google_sql_database" "database" {
  name     = "pr_helper"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "pr_user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Memorystore Redis instance
resource "google_redis_instance" "cache" {
  name               = "pr-helper-redis-${var.environment}"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  authorized_network = google_compute_network.vpc.id
  redis_version      = "REDIS_7_0"
  display_name       = "PR Helper Redis Cache"
  auth_enabled       = true

  depends_on = [google_project_service.apis]
}

# Secret Manager secrets
resource "google_secret_manager_secret" "django_secret_key" {
  secret_id = "django-secret-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "github_client_id" {
  secret_id = "github-client-id"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "github_client_secret" {
  secret_id = "github-client-secret"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "tailscale_auth_key" {
  secret_id = "tailscale-auth-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

# Cloud Run service for web application
resource "google_cloud_run_service" "web" {
  name     = "pr-helper-web"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      containers {
        image = var.web_image

        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "PORT"
          value = "8080"
        }

        env {
          name  = "DEBUG"
          value = "False"
        }

        env {
          name  = "USE_CLOUD_SQL_CONNECTOR"
          value = "True"
        }

        env {
          name  = "CLOUD_SQL_CONNECTION_NAME"
          value = google_sql_database_instance.postgres.connection_name
        }

        env {
          name  = "DB_NAME"
          value = google_sql_database.database.name
        }

        env {
          name  = "DB_USER"
          value = google_sql_user.user.name
        }

        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = "db-password"
              key  = "latest"
            }
          }
        }

        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.django_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GITHUB_CLIENT_ID"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.github_client_id.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GITHUB_CLIENT_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.github_client_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "CELERY_BROKER_URL"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name  = "ALLOWED_HOSTS"
          value = var.allowed_hosts
        }

        env {
          name  = "TAILSCALE_ENABLED"
          value = var.tailscale_enabled ? "true" : "false"
        }

        env {
          name = "TAILSCALE_AUTH_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.tailscale_auth_key.secret_id
              key  = "latest"
            }
          }
        }

        startup_probe {
          http_get {
            path = "/health/"
          }
          initial_delay_seconds = 10
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health/"
          }
          initial_delay_seconds = 30
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"        = "0"
        "autoscaling.knative.dev/maxScale"        = "10"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.id
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.apis,
    google_sql_database_instance.postgres,
    google_redis_instance.cache
  ]
}

# Cloud Run service for Celery worker
resource "google_cloud_run_service" "worker" {
  name     = "pr-helper-worker"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      containers {
        image = var.worker_image

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "USE_CLOUD_SQL_CONNECTOR"
          value = "True"
        }

        env {
          name  = "CLOUD_SQL_CONNECTION_NAME"
          value = google_sql_database_instance.postgres.connection_name
        }

        env {
          name  = "DB_NAME"
          value = google_sql_database.database.name
        }

        env {
          name  = "DB_USER"
          value = google_sql_user.user.name
        }

        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = "db-password"
              key  = "latest"
            }
          }
        }

        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.django_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GITHUB_CLIENT_ID"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.github_client_id.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GITHUB_CLIENT_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.github_client_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "CELERY_BROKER_URL"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name  = "CELERY_RESULT_BACKEND"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name  = "TAILSCALE_ENABLED"
          value = var.tailscale_enabled ? "true" : "false"
        }

        env {
          name = "TAILSCALE_AUTH_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.tailscale_auth_key.secret_id
              key  = "latest"
            }
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"        = "1"
        "autoscaling.knative.dev/maxScale"        = "5"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.id
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.apis,
    google_sql_database_instance.postgres,
    google_redis_instance.cache
  ]
}

# IAM policy to keep services internal (no public access)
resource "google_cloud_run_service_iam_member" "noauth_web" {
  count    = var.allow_public_access ? 1 : 0
  service  = google_cloud_run_service.web.name
  location = google_cloud_run_service.web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Monitoring uptime check
resource "google_monitoring_uptime_check_config" "health_check" {
  count        = var.enable_monitoring ? 1 : 0
  display_name = "pr-helper-uptime-check"
  timeout      = "10s"
  period       = "300s"

  http_check {
    path         = "/health/"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_service.web.status[0].url, "https://", "")
    }
  }
}

# Alert policy for error rate
resource "google_monitoring_alert_policy" "error_rate" {
  count        = var.enable_monitoring ? 1 : 0
  display_name = "PR Helper High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate above 5%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"pr-helper-web\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.notification_channels

  alert_strategy {
    auto_close = "1800s"
  }
}

# Outputs
output "web_service_url" {
  value       = google_cloud_run_service.web.status[0].url
  description = "URL of the web service"
}

output "worker_service_name" {
  value       = google_cloud_run_service.worker.name
  description = "Name of the worker service"
}

output "sql_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "Cloud SQL connection name"
}

output "redis_host" {
  value       = google_redis_instance.cache.host
  description = "Redis host IP"
}

output "vpc_connector_id" {
  value       = google_vpc_access_connector.connector.id
  description = "VPC Access Connector ID"
}