output "storage_bucket_raw_url" {
  description = "The URL of the raw storage bucket."
  value       = google_storage_bucket.raw.url
}

output "storage_bucket_stage_url" {
  description = "The URL of the stage storage bucket."
  value       = google_storage_bucket.stage.url
}

output "storage_bucket_dependencies_url" {
  description = "The URL of the dependencies storage bucket."
  value       = google_storage_bucket.dependencies.url
}

output "artifact_registry_repository_id" {
  description = "ID of the repository in Artifact Registry."
  value       = google_artifact_registry_repository.docker.id
}

output "cloud_run_service_batchingestor_url" {
  description = "URL of the batch ingest Cloud Run service."
  value       = google_cloud_run_service.batch_ingest_api.status.0.url
}

output "compute_network_vpc_id" {
  description = "ID of the created VPC network."
  value       = google_compute_network.vpc.id
}

output "compute_subnetwork_vm_subnet_id" {
  description = "ID of the created subnetwork in the VPC network."
  value       = google_compute_subnetwork.vm_subnet.id
}
