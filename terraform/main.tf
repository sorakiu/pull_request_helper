terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_service" "pr_helper" {
  name     = "pr-helper"
  location = var.region

  template {
    spec {
      containers {
        image = var.docker_image
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@${google_sql_database.database.instance}/${google_sql_database.database.name}"
        }
        env {
          name  = "SECRET_KEY"
          value = var.secret_key
        }
        env {
          name  = "GITHUB_CLIENT_ID"
          value = var.github_client_id
        }
        env {
          name  = "GITHUB_CLIENT_SECRET"
          value = var.github_client_secret
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_sql_database_instance" "postgres" {
  name             = "pr-helper-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"
  }
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