output "storage_bucket_raw_url" {
  description = "The URL of the raw storage bucket."
  value       = google_storage_bucket.raw.url
}

output "storage_bucket_stage_url" {
  description = "The URL of the stage storage bucket."
  value       = google_storage_bucket.stage.url
}

output "artifact_registry_repository_id" {
  description = "ID of the repository in Artifact Registry."
  value       = google_artifact_registry_repository.docker.id
}
