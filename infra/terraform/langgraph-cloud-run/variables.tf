variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and Artifact Registry"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "resume-langgraph-api"
}

variable "repository_id" {
  description = "Artifact Registry repository id"
  type        = string
  default     = "resume-services"
}

variable "image" {
  description = "Container image URL to deploy (e.g. REGION-docker.pkg.dev/PROJECT/REPO/langgraph:tag)"
  type        = string
}

variable "allow_unauthenticated" {
  description = "Whether to allow public access to Cloud Run service"
  type        = bool
  default     = true
}

variable "cpu" {
  description = "CPU limit for container"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit for container"
  type        = string
  default     = "1Gi"
}

variable "min_instance_count" {
  description = "Minimum Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instance_count" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 3
}
