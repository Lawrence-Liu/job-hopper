output "service_url" {
  description = "Deployed Cloud Run URL"
  value       = google_cloud_run_v2_service.langgraph_api.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}

output "service_account_email" {
  description = "Runtime service account email"
  value       = google_service_account.run_sa.email
}
