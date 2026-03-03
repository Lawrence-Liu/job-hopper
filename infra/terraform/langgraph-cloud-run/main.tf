locals {
  service_account_id = replace("${var.service_name}-sa", "_", "-")
}

resource "google_project_service" "required" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "repo" {
  project       = var.project_id
  location      = var.region
  repository_id = var.repository_id
  description   = "Container images for resume services"
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}

resource "google_service_account" "run_sa" {
  project      = var.project_id
  account_id   = local.service_account_id
  display_name = "${var.service_name} runtime service account"

  depends_on = [google_project_service.required]
}

resource "google_project_iam_member" "run_sa_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_cloud_run_v2_service" "langgraph_api" {
  name                = var.service_name
  location            = var.region
  project             = var.project_id
  deletion_protection = false

  template {
    service_account = google_service_account.run_sa.email

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }

    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_service_account.run_sa,
    google_project_iam_member.run_sa_vertex_user,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.langgraph_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
