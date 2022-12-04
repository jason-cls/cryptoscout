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

output "cloud_run_service_batchingestor_url" {
  description = "URL of the batch ingest Cloud Run service."
  value       = google_cloud_run_service.batch_ingest_api.status.0.url
}
