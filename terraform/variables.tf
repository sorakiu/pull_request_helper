variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, production)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "web_image" {
  description = "Docker image for web Cloud Run service"
  type        = string
}

variable "worker_image" {
  description = "Docker image for worker Cloud Run service"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "allowed_hosts" {
  description = "Comma-separated list of allowed hosts for Django"
  type        = string
  # No default - require explicit configuration for security
}

variable "allow_public_access" {
  description = "Allow public access to web service (false for internal VPC only)"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring uptime checks and alerts"
  type        = bool
  default     = true
}

variable "tailscale_enabled" {
  description = "Enable optional Tailscale connection for private access"
  type        = bool
  default     = false
}

variable "tailscale_auth_key" {
  description = "Tailscale auth key for authentication (required when tailscale_enabled=true)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "notification_channels" {
  description = "List of notification channel IDs for alerting"
  type        = list(string)
  default     = []
}